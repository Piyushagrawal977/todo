from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

class Book():
    id:int
    title:str
    author:str
    description:str
    rating:int

    def __init__(self,id,title,author,description,rating):
        self.id=id
        self.title=title
        self.author=author
        self.description=description
        self.rating=rating

class BookRequest(BaseModel):
    id:Optional[int]=Field(description="Id is not required", default=None)
    title:str = Field(min_length=3)
    author:str = Field(min_length=1)
    description:str = Field(min_length=1, max_length=100) 
    rating:int = Field(gt=0,lt=6)

    model_config={
        "json_schema_extra":{
            "example":{
                "title":"A new book",
                "author": "Greatest Author",
                "description": " A new description of a book",
                "rating": 2
            }
        }
    }


BOOKS = [

    Book(1,"Computer Science","Author 1","Great Book",5),
    Book(2,"Fast with FastAPI","Author 1","Knowledgable content",4),
    Book(3,"first line of your code","Author 1","Interesting book",3),
    Book(4,"hello world","Author 2","Book description",2),
    Book(5,"Master of AI","Author 3","Book description",1)
]



@app.get("/books")
async def read_all_books():
    return  BOOKS

@app.get("/books/{book_id}")
async def read_book(book_id:int):
    for book in BOOKS:
        if book.id==book_id:
            return book 
        
@app.get("/books/")
async def read_book(book_rating:int):
    list_of_books=[]
    for book in BOOKS:
        if book.rating==book_rating:
            list_of_books.append(book)
    return list_of_books
        

@app.post("/create_book")
async def create_book(book_request:BookRequest):
    # print(book_request.model_dump)
    new_book=Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))
    return "you added new book succesfully"

def find_book_id(book: Book):
    book.id= 1 if len(BOOKS) == 0 else BOOKS[-1].id+1
    return book