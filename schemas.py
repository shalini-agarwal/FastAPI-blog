from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)

class UserCreate(UserBase):
    #password field - this is what we recieve from the user after they register
    password:str = Field(min_length=8)

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_file: str | None
    image_path: str

class UserPrivate(UserPublic):
    email: EmailStr # when we return post data, we won't be exposing the the user (Author's) email which is a privacy improvement

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)
    image_file: str | None = Field(default=None, min_length=1, max_length=200) # only storing the image filename and not the path as the image_path property in the model above will build the complete path for the image file

class Token(BaseModel):
    access_token: str
    token_type: str

class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100) # haven't given any default values here, that means these fields are required
    content: str = Field(min_length=1)

class PostCreate(PostBase): # this defines what we accept when creating a new post
    user_id: int #TEMP because when we add authorization, we are going to get the user_id from the session

'''  Added None because we want to keep it optional as it is for PATCH update.
    Didn't include user_id here because we typically don't want to allow a change of ownership through a partial endpoint.
    If we do want to allow change of ownership, we would want to have it either through a PUT request or have a dedicated endpoint for ownership transfer.
'''
class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100) 
    content: str | None = Field(default=None, min_length=1)

class PostResponse(PostBase): # this defines what we return from our API end point; this includes fields/ attributes which are not provided by our client
    model_config = ConfigDict(from_attributes=True) # this allows Pydantic to read from databases along with dictionaries; basically by default Pydantic can read dictionary key-value pairs but setting from_attribute=True allows it to access values from dot notation as well

    id: int
    user_id: int
    date_posted: datetime
    author: UserPublic
