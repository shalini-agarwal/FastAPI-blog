from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_file: str | None
    image_path: str

class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100) # haven't given any default values here, that means these fields are required
    content: str = Field(min_length=1)

class PostCreate(PostBase): # this defines what we accept when creating a new post
    user_id: int #TEMP because when we add authorization, we are going to get the user_id from the session


class PostResponse(PostBase): # this defines what we return from our API end point; this includes fields/ attributes which are not provided by our client
    model_config = ConfigDict(from_attributes=True) # this allows Pydantic to read from databases along with dictionaries; basically by default Pydantic can read dictionary key-value pairs but setting from_attribute=True allows it to access values from dot notation as well

    id: int
    user_id: int
    date_posted: datetime
    author: UserResponse
