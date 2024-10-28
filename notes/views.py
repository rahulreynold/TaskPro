from django.shortcuts import render,redirect

from django.views.generic import View

from notes.forms import TaskForm,User,RegistrationForm,SignInForm

from django.contrib import messages

from notes.models import Task

from django import forms

from django.db.models import Q

from django.db.models import Count

from django.contrib.auth.models import User

from django.contrib.auth import authenticate,login,logout

class TaskCreateView(View):
    
    def get(self,request,*args,**kwargs):

        form_instance=TaskForm()

        return render(request,"task_create.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance=TaskForm(request.POST)

        if form_instance.is_valid():

            form_instance.save()

            messages.success(request,"Task has been added successfully")

            return redirect("task-list")
           
        
        else:

            messages.error(request,"failed to ask task")
            
            return render(request,"task_create.html",{"form":form_instance})
        


# class TaskListView(View):

#     def get(self,request,*args,**kwargs):

#         # query for fetching
#         qs=Task.objects.all()

#         if "category" in request.GET:
#             category_value=request.GET.get("category")

#             # qs=qs.filter(category=category_value)
#             qs=Task.objects.filter(category=category_value)

#             if category_value == "all":
#                 qs=Task.objects.all
            
            
#         return render(request,"tasks_list.html",{"tasks":qs,"selected":request.GET.get("category","all")})
    

class TaskListView(View):
    def get(self,request,*args,**kwargs):

        search_text=request.GET.get("search_text")

        selected_category=request.GET.get("category","all")     

        if selected_category=="all":
            qs=Task.objects.all()
        else:
            qs=Task.objects.filter(category=selected_category)

        if search_text != None:
            qs=Task.objects.filter(
                Q(title__contains=search_text)|
                Q(description__contains=search_text)
            )


        return render(request,"tasks_list.html",{"tasks":qs,"selected":selected_category})

   
class TaskDetailedView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        qs=Task.objects.get(id=id)

        return render(request,"task_detail.html",{"task":qs})


class TaskUpdateView(View):

    def get(self,request,*args,**kwargs):

        # extract pk from kwargs
        id=kwargs.get("pk")

        task_obj=Task.objects.get(id=id)

        # initialize taskform with taskobj
        form_instance=TaskForm(instance=task_obj)

        # adding status filed to forminstace
        form_instance.fields["status"]=forms.ChoiceField(choices=Task.status_choices,widget=forms.Select(attrs={"class":"form-control form-select"}),initial=task_obj.status)

        return render(request,"task_edit.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        # id extraction
        id=kwargs.get("pk")

        # fetch task object with id
        task_obj=Task.objects.get(id=id)

        # initialize form instance with request.POST and instance
        form_instance=TaskForm(request.POST,instance=task_obj)

        #check form has no errors
        if form_instance.is_valid():

            #add status to form instance
            form_instance.instance.status=request.POST.get("status")

             #save from instance
            form_instance.save()

            return redirect("task-list")
        
        else:
            return render(request,"task_edit.html",{"form":form_instance})
            

        

class TaskDeleteView(View):

    def get(self,request,*args,**kwargs):

        # extract id and delete task object with this id
        Task.objects.get(id=kwargs.get("pk")).delete()

        return redirect("task-list")
    

class TaskSummaryView(View):

    def get(self,request,*args,**kwargs):
        qs=Task.objects.all()
        total_task_count=qs.count()

        category_summary=Task.objects.all().values("category").annotate(cat_count=Count("category"))

        # category_summary = Task.objects.filter(status="completed").values("category").annotate(Count("category"))

        status_summary=Task.objects.all().values("status").annotate(cat_status=Count("status"))

        print(category_summary)
        # print(status_summary)

        context={
            "total_task_count":total_task_count,
            "category_summary":category_summary,
            "status_summary":status_summary,

        }
        return render(request,"summary.html",context)
    
class SignUpView(View):

    template_name="register.html"

    def get(self,request,*args,**kwargs):

        form_instance=RegistrationForm

        return render(request,self.template_name,{"form":form_instance})
    

    def post(self,request,*args,**kwargs):

        form_instance=RegistrationForm(request.POST)

        if form_instance.is_valid():

            data=form_instance.cleaned_data

            User.objects.create_user(**data)

            return redirect("signin")
        else:
            return render(request,self.template_name,{"form":form_instance})
        
class SignInView(View):

    template_name="login.html"

    def get(self,request,*args,**kwargs):

        form_instance=SignInForm()

        return render(request,self.template_name,{"form":form_instance})

    def post(self,request,*args,**kwargs):

        #initialise from with resquest.POST

        form_instance=SignInForm(request.POST)

        if form_instance.is_valid():

            uname=form_instance.cleaned_data.get("username")
            pwd=form_instance.cleaned_data.get("password")

            #authenticate user
            user_object=authenticate(request,username=uname,password=pwd)

            if user_object:

                login(request,user_object)

                return redirect("task-list")

            return render(request,self.template_name,{"form":form_instance})
        

class SignOutView(View):

    def get(self,request,*args,**kwargs):

        logout(request)

        return redirect("signin")
    
    
    





        
            