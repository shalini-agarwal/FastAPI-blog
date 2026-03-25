from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate, PaginatedPostsResponse

from auth import CurrentUser

router = APIRouter()

'''
A few things to note-
Pydantic will automatically serialize the author-relationship as a user response.
Adding response_model parameter so that FastAPI validates that the response structure matches the given schema; over here it is PaginatedPostsResponse.
Adding Annoted syntax with Query to implement constraints -
    For skip, the Query is greater than or equal to 0 (ge=0) because we don't negavtive offsets. The default is zero which means if no skip is provided, then we start at the beginning.
    For limit, the Query >=1 and <=100. This means we don't want someone to request for 0 or negative post and the cap of 100 is to prevent someone from requesting a million or so posts and exhausting the resources in grabbing everything.
    The default for limit is 10 because that's a reasonable batch size for how many posts someone would want.
PS. We are doing skip and limit and not something like page and per-page because this is more fexible & gives more control and is also common across REST api architectures.
'''
@router.get("", response_model=PaginatedPostsResponse)
async def get_posts(
    db: Annotated[AsyncSession, Depends(get_db)], 
    skip: Annotated[int, Query(ge=0)] = 0, 
    limit: Annotated[int, Query(ge=1, le=100)] = 10):
    
    count_result = await db.execute(select(func.count()).select_from(models.Post))
    total = count_result.scalar() or 0

    
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc()) # this is very important for pagination. If we don't order our results, then the db can return the result in any order and this means the same skip & limit values can give different results on different requests. 
        .offset(skip) #offset tells the db to skip that many records
        .limit(limit))#limit tells to provide atmost that many records
    posts = result.scalars().all()

    has_more = skip + len(posts) < total #if the number of posts skipped + the number of posts returned in this call is less than the total posts in the db, then that means there are more posts. This will give has_more a True else it'll be False.
    
    return PaginatedPostsResponse(
        posts=[PostResponse.model_validate(post) for post in posts], #normally when FastAPI handles the response model, it does this conversion automatically but here we're constructing the response object ourselves, hence we need to handle the conversion manually.This ensures that all the nested relationships like author are properly serialized.
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


# By adding the current_user dependency, this route is protected. If someone tries to call this endpoint without a valid token, they will get a 401 unauthorized before the fucntion even runs.
@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id # this comes from the authenticated token instead of the api request body
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
async def update_post_full(post_id: int, post_data: PostCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # 401 is unauthorized, that means you are not authenticated, i.e. if there is a missing or invalid token.
    # 403 means you're authenticated but you don't have permission for this action.
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this post")

    post.title = post_data.title
    post.content = post_data.content

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(post_id: int, post_data: PostUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this post")

    # exclude_unset attribute only sets the values which were sent in the api request; it is essential because otherwise it will set all the values not sent in the request to default values
    update_data = post_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(post, field, value) # this sets the attribute 'field' in the post to the provided 'value'

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


# For DELETE requests, we usually return a 204 No Content Response which means that the request succeeded but there is no response body. Hence we don't have a response_model here.
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT )
async def delete_post(post_id: int, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]): # using type hinting helps FastAPI to automatically validate the input
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this post")

    await db.delete(post)
    await db.commit()
