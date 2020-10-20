from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, logout, authenticate
from pokuty.forms import UserAdminCreationForm, LoginForm
from django.views import generic
from django.urls import reverse
from django.utils import dateparse
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Penalty, PenaltyRecord, Income, Expense, Fridge
from django.db.models import Sum

def expense(request):
    return render(request, "pokuty/expense.html")

def expenseSave(request):
    selectedDate = request.POST.get('date')
    price = request.POST.get('price')
    reason = request.POST.get('reason')
    new_record = Expense(expenseDate= selectedDate,reason=reason,  
            price=price)
    new_record.save()
    return render(request, "pokuty/dashboard.html")

def fridge(request):
    users=CustomUser.objects.all()
    return render(request, "pokuty/fridge.html", {'users':users})

def fridgeSave(request):
    selectedDate = request.POST.get('date')
    userid = request.POST.get('user')
    price = request.POST.get('price')
    selecteduser = CustomUser.objects.get(id=userid)
    username = selecteduser.first_name +' '+ selecteduser.last_name
    new_record = PenaltyRecord(penaltyDate= selectedDate,userId=selecteduser.id, user=username, penaltyName="Lednice", 
            penaltyPrice=price, payed=False)
    new_record.save()
    return render(request, "pokuty/dashboard.html" )

def income(request):
    users=CustomUser.objects.all()
    return render(request, "pokuty/income.html", {'users':users})

def incomeSave(request):
    selectedDate = request.POST.get('date')
    price = int( request.POST.get('price'))
    userid = request.POST.get('user')
    selecteduser = CustomUser.objects.get(id=userid)
    username = selecteduser.first_name +' '+ selecteduser.last_name
    new_record = Income(incomeDate= selectedDate,userID=userid, user=username,  
            price=price)
    new_record.save()
    while price > 0:
        dbrecord= PenaltyRecord.objects.filter(userId=userid).filter(payed=False).first()
        if dbrecord !=None or int(dbrecord.penaltyPrice) < price :
            dbrecord.payed = True
            dbrecord.save()
            price -= dbrecord.penaltyPrice
  
    return render(request, "pokuty/dashboard.html")

def listview(request):
    records = PenaltyRecord.objects.all().filter(payed=False)
    incomes = Income.objects.all()
    expenses = Expense.objects.all()
    return render(request, "pokuty/listview.html",{'records':records, 'incomes':incomes, 'expenses':expenses})

def teamsave(request):
    selectedusers = request.POST.getlist('user')
    selectedDate = request.POST.get('date')
    for user in selectedusers:
        userid = int(user)
        selecteduser = CustomUser.objects.get(id=userid)
        username = selecteduser.first_name +' '+ selecteduser.last_name
        penaltyId = int(request.POST.get('penalty'))
        penaltyItem = Penalty.objects.get(id=penaltyId)
        new_record = PenaltyRecord(penaltyDate= selectedDate,userId=user, user=username, penaltyName=penaltyItem.name, 
            penaltyPrice=penaltyItem.price, payed=False)
        new_record.save()
    
    return render(request, "pokuty/dashboard.html" )

def indsave(request):
    selectedpenalty = request.POST.getlist('penalty')
    selectedDate = request.POST.get('date')
    userid = request.POST.get('user')
    selecteduser = CustomUser.objects.get(id=userid)
    username = selecteduser.first_name +' '+ selecteduser.last_name
    for penalty in selectedpenalty:
        penaltyId = penalty
        penaltyItem = Penalty.objects.get(id=penaltyId)
        new_record = PenaltyRecord(penaltyDate= selectedDate,userId=selecteduser.id, user=username, penaltyName=penaltyItem.name, 
            penaltyPrice=penaltyItem.price, payed=False)
        new_record.save()
    #return render(request, "pokuty/dashboard.html" )
    return redirect('dashboard')

def indTraining(request):
    users=CustomUser.objects.all()
    pokuty = Penalty.objects.all().filter(trainingPenalty=True).filter(teamPenalty=False)
    return render(request,"pokuty/individual.html",{'users': users, 'pokuty':pokuty})

def teamTraining(request):
    users=CustomUser.objects.all()
    pokuty = Penalty.objects.all().filter(trainingPenalty=True).filter(teamPenalty=True)
    return render(request,"pokuty/team.html",{'users': users, 'pokuty':pokuty})

def indMatch(request):
    users=CustomUser.objects.all()
    pokuty = Penalty.objects.all().filter(trainingPenalty=False).filter(teamPenalty=False)
    return render(request,"pokuty/individual.html",{'users': users, 'pokuty':pokuty})

def teamMatch(request):
    users=CustomUser.objects.all()
    pokuty = Penalty.objects.all().filter(trainingPenalty=False).filter(teamPenalty=True)
    return render(request,"pokuty/team.html",{'users': users, 'pokuty':pokuty})

def register(request):
    if request.method == "GET":
        return render(
            request, "register.html",
            {"form": UserAdminCreationForm}
        )
    elif request.method == "POST":
        form = UserAdminCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("dashboard"))

@login_required(login_url='login')
def dashboard(request):
    income= Income.objects.aggregate(Sum('price'))
    expenses= Expense.objects.aggregate(Sum('price'))
    notpay= PenaltyRecord.objects.filter(payed=False).aggregate(Sum('penaltyPrice'))
    if income==None:
        a=0
    else:
        a= int(income.get('price__sum'))
    if expenses==None:
        b=0
    else:
        b= int(expenses.get('price__sum'))
    
    bank= a - b
    return render(request, "pokuty/dashboard.html", {'income':income, 'expenses':expenses, 'notpay':notpay, 'bank':bank} )
    
class UzivatelViewLogin(generic.edit.CreateView):
    form_class = LoginForm
    template_name = "registration/login2.html"

    def get(self, request):
        if request.user.is_authenticated:
            messages.info(request, "Už jsi přihlášený, nemůžeš se přihlásit znovu.")
            return redirect(reverse("dashboard"))
        else:
            form = self.form_class(None)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        if request.user.is_authenticated:
            messages.info(request, "Už jsi přihlášený, nemůžeš se přihlásit znovu.")
            return redirect(reverse("dashboard"))
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(email = email, password = password)
            if user:
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, "Tento účet neexistuje.")
        return render(request, self.template_name, {"form": form})
		
def logout_user(request):
     if request.user.is_authenticated:
        logout(request)
     else:
        messages.info(request, "Nemůžeš se odhlásit, pokud nejsi přihlášený.")
     return redirect(reverse("login"))