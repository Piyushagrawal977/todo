from fastapi import Body, FastAPI
app = FastAPI()

books=[
    {"title":"title one","author":"author one","category":"Science"},
    {"title":"title two","author":"author two","category":"math"},
    {"title":"title three","author":"author three","category":"geography"},
    {"title":"title four","author":"author four","category":"science"},
    {"title":"title five","author":"author five","category":"English"},
    
]

@app.get("/books")
async def read_all_books():
    return books

@app.get("/book/mybook")
async def mybook():
    return "my favourite book "

@app.get("/book/{book_title}")
async def book(book_title:str):
    for book in books:
        if book.get('title').casefold() == book_title.casefold():
            return book
    return "no as such book is available"

@app.get("/book")
async def book(category:str):
    list_of_books=[]
    for book in books:
        if book.get('category').casefold() == category.casefold():
            list_of_books.append(book)
    return list_of_books

@app.get("/book/{author_title}/")
async def book(author_title:str, category:str):
    list_of_books=[]
    for book in books:
        if book.get("author") == author_title.casefold() and book.get('category').casefold() == category.casefold():
            list_of_books.append(book)
    return list_of_books

@app.post("/books/add")
async def add_book(newBook=Body()):
    books.append(newBook)
    return "you successfully added new book"

@app.put("/book/update")
async def update_book(updateBook = Body()):
    for i in range (len(books)):
        if books[i].get('title').casefold()==updateBook.get('title').casefold():
            books[i]=updateBook
    return "book sucessfully updated"

@app.delete("/book/delete")
async def delete_book(book_title:str):
    for i in range(len(books)):
        if books[i].get('title').casefold()==book_title.casefold():
            books.pop(i)
            return "successfully deleted"

@app.get("/books/{author_title}")
async def fetch_author(author_title:str):
    list_of_author=[]
    for book in books:
        if book.get("author").casefold()==author_title.casefold():
            list_of_author.append(book)
    return list_of_author
