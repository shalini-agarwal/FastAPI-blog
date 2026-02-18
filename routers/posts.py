from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate

router = APIRouter()


# ??? Pydantic will automatically serialize the author-relationship as a user response (44:10 ?)
@router.get("", response_model=list[PostResponse]) #adding response_model parameter so that FstAPI validates that the response structure matches the PostResponse schema
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).order_by(models.Post.date_posted.desc()))
    posts = result.scalars().all()
    return posts

@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id
    )

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"]) # When we create a new post and return it, we need the author to be loaded for the post response. So instead of doing a separate query with selectinload, we can tell refresh to also load specific relationships using the attribute name parameter.

    return new_post

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]): # using type hinting helps FastAPI to automatically validate the input
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()

    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

# this endpoint is for a PUT request which requires all the information to be provided for an update; Hence, we will be using PostCreate instead of PostUpdate because that already requires all the information.
@router.put("/{post_id}", response_model=PostResponse)
async def update_post_full(post_id: int, post_data: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # checking whether the new user_id sent by the PUT request exists; we will only do this if the client sent a user_id which is different from what was already present in the original post
    # we only want to allow users who created a post to update or delete them
    if post_data.user_id != post.user_id:
        result = await db.execute(select(models.User).where(models.User.id == post_data.user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(post_id: int, post_data: PostUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # exclude_unset attribute only sets the values which were sent in the api request; it is essential because otherwise it will set all the values not sent in the request to default values
    update_data = post_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(post, field, value) # this sets the attribute 'field' in the post to the provided 'value'

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


# For DELETE requests, we usually return a 204 No Content Response which means that the request succeeded but there is no response body. Hence we don't have a response_model here.
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT )
async def delete_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]): # using type hinting helps FastAPI to automatically validate the input
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    await db.delete(post)
    await db.commit()
# Later when we add authentication, we'll add ownership checks so that only the author of the post is allowed to delete it.
