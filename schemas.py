from pydantic import BaseModel, ConfigDict, Field

class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100) # haven't given any default values here, that means these fields are required
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50)

class PostCreate(PostBase): # this defines what we accept when creating a new post
    pass

class PostResponse(PostBase): # this defines what we return from our API end point; this includes fields/ attributes which are not provided by our client
    model_config = ConfigDict(from_attributes=True) # this allows Pydantic to read from databases along with dictionaries; basically by default Pydantic can read dictionary key-value pairs but setting from_attribute=True allows it to access values from dot notation as well

    id: int
    date_posted: str
