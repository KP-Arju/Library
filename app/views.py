from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import Book
from django.contrib import messages
from django.contrib.auth.models import auth, User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from datetime import date
from django.core.paginator import Paginator
# Create your views here.
@login_required(login_url='login')
def HomePage(request):
    return render (request,'homepage.html')
def SignupPage(request):
   if request.method=='POST':
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')
        if pass1!=pass2:
         return HttpResponse("Your password and confirm password are not Same!!")
        else:

            my_user=User.objects.create_user(uname,email,pass1)
            my_user.save()
            return redirect('login')
        
        
   return render (request,'signuppage.html')  
def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
         login(request,user)
         return redirect('home')
        else:
            return HttpResponse ("Username or Password is incorrect!!!")
       
        
    return render (request,'loginpage.html')
def LogoutPage(request):
    logout(request)
    return redirect('login')
# Register view to register user
def register(request):
    # If request is post then get user details from request
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        # Check if password and confirm password matches
        if password1 == password2:
            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already exist")
                return redirect("register")
            # Check if email already exists
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email already registered")
                return redirect("register")
            # If username and email does not exists then create user
            else:
                # Create user
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=password1,
                )
                # Save user
                user.save()
                # Redirect to login page
                return redirect("login")
        else:
            # If password and confirm password does not matches then show error message
            messages.info(request, "Password not matches")
            return redirect("register")
    else:
        # If request is not post then render register page
        return render(request, "register.html")
# Logout view to logout user
def logout(request):
    # Logout user and redirect to home page
    auth.logout(request)
    return redirect("/")
# Issue view to issue book to user
@login_required(login_url="login")
def issue(request):
    # If request is post then get book id from request
    if request.method == "POST":
        book_id = request.POST["book_id"]
        current_book = Book.objects.get(id=book_id)
        book = Book.objects.filter(id=book_id)
        issue_item = IssuedItem.objects.create(
            user_id=request.user, book_id=current_book
        )
        issue_item.save()
        book.update(quantity=book[0].quantity - 1)
        # Show success message and redirect to issue page
        messages.success(request, "Book issued successfully.")
    # Get all books which are not issued to user
    my_items = IssuedItem.objects.filter(
        user_id=request.user, return_date__isnull=True
    ).values_list("book_id")
    books = Book.objects.exclude(id__in=my_items).filter(quantity__gt=0)
    # Return issue page with books that are not issued to user
    return render(request, "issue_item.html", {"books": books})
# History view to show history of issued books to user
@login_required(login_url="login")
def history(request):
    # Get all issued books to user
    my_items = IssuedItem.objects.filter(user_id=request.user).order_by("-issue_date")
    # Paginate data
    paginator = Paginator(my_items, 10)
    # Get page number from request
    page_number = request.GET.get("page")
    show_data_final = paginator.get_page(page_number)
    # Return history page with issued books to user
    return render(request, "history.html", {"books": show_data_final})
# Return view to return book to library
@login_required(login_url="login")
def return_item(request):
    # If request is post then get book id from request
    if request.method == "POST":
        # Get book id from request
        book_id = request.POST["book_id"]
        # Get book object
        current_book = Book.objects.get(id=book_id)
        # Update book quantity
        book = Book.objects.filter(id=book_id)
        book.update(quantity=book[0].quantity + 1)
        # Update return date of book and show success message
        issue_item = IssuedItem.objects.filter(
            user_id=request.user, book_id=current_book, return_date__isnull=True
        )
        issue_item.update(return_date=date.today())
        messages.success(request, "Book returned successfully.")
    # Get all books which are issued to user
    my_items = IssuedItem.objects.filter(
        user_id=request.user, return_date__isnull=True
    ).values_list("book_id")
    # Get all books which are not issued to user
    books = Book.objects.exclude(~Q(id__in=my_items))
    # Return return page with books that are issued to user
    params = {"books": books}
    return render(request, "return_item.html", params)