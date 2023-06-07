from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# from django.urls import reverse
from django.views import View
from django.utils import translation
from .models import PagesContent, News, NewsComment, Chat, ChatMessage, ChatNotifications, ChatMessageRead
from tms.models import Project, JobInvitation, JobAssignment
from accounting.models import Order, Request, Quote, Invoice, TranslatorInvoice, UserFinancialAccount, TranslatorInvoice, Payment, RequestTargetLanguage
from accounting.models import RequestItem
from translation.models import TranslatorLanguage, TranslatorPrice, ProjectManagerLanguage, Translator, ProjectManager, Customer, AccountManager, VendorManager
from accounts.models import WorkExperience, CustomUser
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q

# models added by zulkifal
from company.models import Company, CompanyLanguage, CompanySpeciality, PlanToDisplay, DefaultSubServicePrice, CompanyService, CompanyPriceException, DefaultServicePrice, CompanyCustomerPriceAgreement, CompanyDeliveryTime, CompanyHoliday, CompanyQualityLevel, CompanyDeliveryTime, CompanyBranch  # ,CompanyCountries
from accounting.filters import RequestFilter, OrderFilter, QuoteFilter, InvoiceFilter, TranslatorInvoiceFilter, CustomerCompanyFinancialAccountFilter, UserFinancialAccountFilter, FinancialTransactionFilter, PaymentFilter, TranslatorPaymentFilter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView

# for chat
from django.template.loader import render_to_string
from django.http import JsonResponse

# For sending emails
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template import Context, Template
from pages.models import EmailTemplate

# For email templates context
from tms.models import Job
from company.models import CompanyBranch, CompanyBranding
from accounting.models import TranslatorInvoice, TranslatorPayment, Request, Order, Quote, Payment
from translation.models import TranslatorPrice, CustomerCompany, CustomerCompanyPrimaryContact

# for reports
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.utils import get_session_company, is_a_company_user


# count the number of files by zulkifal
from django.db.models import Count
# from accounting.utils import get_num_uploaded_files


def white_label_company(request):
    # White labeling
    current_domain = request.META['HTTP_HOST']
    print('-------------- current_domain', current_domain)
    white_label_company = None
    for company_branding in CompanyBranding.objects.all():
        if current_domain == company_branding.domain and company_branding.is_white_label:
            print('Apply branding for ', company_branding.company)
            white_label_company = company_branding.company
            break

    return white_label_company


class Dashboard(View):

    userTemplate = 'pages/dashboard.html'
    othersTemplate = 'pages/dashboard_backup.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):

        user_type = request.user.profile.user_type
        # print(user_type)
        context = {}
        context['white_label_company'] = white_label_company(request)
        
        context['ordersPage'] = 'active'

        session_company = get_session_company(request.session['company_id']) if 'company_id' in request.session else None
        if session_company:
            company = session_company
        else:
            company = Company.objects.get(id=1)

        context['company'] = company

        print("profile id",request.user.profile.id);
        corporates = CustomerCompanyPrimaryContact.objects.filter(primary_contact=request.user.profile)
        print(corporates)
        context['is_corporate_PC'] = 0
        if(len(corporates)):
            context['is_corporate_PC'] = 1
            context['corporate_id'] = corporates[0].customer_company.id #Assuming a person can have one corporate

        userEmail = request.user.profile.user    
        customerName =  CustomUser.objects.filter(email=request.user.profile.user)
        context['firstName'] = customerName[0].first_name
        context['lastName'] = customerName[0].last_name

        # zulkifal - for project name 
        userId = request.user.profile.user.id
        context['projectName'] = Project.objects.all().order_by('-id')

        if user_type == 'PM':
            print('project manager')
            # Pass own and avaiable projects
            project_manager = ProjectManager.objects.get(profile=request.user)
            context['owner'] = project_manager
            context['pm_projects'] = Project.objects.filter(order__quote_price__quote__request__company=company).order_by('-id')
            context['pm_languages'] = ProjectManagerLanguage.objects.filter(project_manager=project_manager.id)
            context['pm_work_experience'] = WorkExperience.objects.filter(user=request.user)
        elif user_type == 'AM':
            account_manager = AccountManager.objects.get(profile=request.user)
            context['owner'] = account_manager
        elif user_type == 'VM':
            vendor_manager = VendorManager.objects.get(profile=request.user)
            context['owner'] = vendor_manager
        elif user_type == 'TR':
            print('translator')
            # Pass own jobs and invoices
            translator = Translator.objects.get(profile=request.user)
            context['owner'] = translator
            context['tr_jobs_assignments'] = JobAssignment.objects.filter(translator=translator, is_active=True).order_by('-id')
            context['tr_jobs_invitations'] = JobInvitation.objects.all().order_by('-id')
            context['tr_languages'] = TranslatorLanguage.objects.filter(translator=translator.id)
            context['tr_prices'] = TranslatorPrice.objects.filter(translator=translator.id)
            context['tr_work_experience'] = WorkExperience.objects.filter(user=request.user)
            context['tr_payments'] = TranslatorPayment.objects.filter(translator_order_id__translator=translator)

            if not UserFinancialAccount.objects.filter(user=request.user).exists():
                UserFinancialAccount.objects.create(user=request.user)

            context['tr_account_balance'] = UserFinancialAccount.objects.filter(user=request.user).first().balance
            context['tr_bills'] = TranslatorInvoice.objects.filter(translator_order_id__translator=translator).order_by('-id')
        elif user_type == 'CU':
            print('Customer')
            # Pass own orders and invoices
            customer = Customer.objects.get(profile=request.user)
            if(customer.customer_company != None):
                customer_company = CustomerCompany.objects.get(id=customer.customer_company.id)
                context['credit_line'] = customer_company.credit_limit + customer_company.credit_note + customer_company.pre_payment
            else:
                context['credit_line']= customer.pre_payment + customer.credit_limit + customer.credit_note 
            context['owner'] = customer

            # zk - dynamic pagination
            records_per_page = int(request.GET.get('records_per_page', 20))

            # for orders Active Data
            ordersActiveQuerySet = Order.objects.filter(Q(delivery_status='I') | Q(delivery_status='N'), quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, payment_status='P').order_by('-id')
            paginator = Paginator(ordersActiveQuerySet, records_per_page)
            page_number = request.GET.get('page')
            context['ordersActiveData'] = paginator.get_page(page_number)

            context['records_per_page'] = records_per_page
            context['ordersActiveTabCount'] = Order.objects.filter(Q(delivery_status='I') | Q(delivery_status='N'), quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, payment_status='P').count()

            # for orders Delivered Data
            ordersDeliveredQuerySet = Order.objects.filter(quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, delivery_status='D').order_by('-id')
            paginator = Paginator(ordersDeliveredQuerySet, records_per_page)
            page_number = request.GET.get('page')
            context['ordersDeliveredData'] = paginator.get_page(page_number)

            context['records_per_page'] = records_per_page
            context['ordersDeliveredTabCount'] = Order.objects.filter(quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, delivery_status='D').count()

            # for orders All Data
            ordersAllQuerySet = Order.objects.filter(Q(delivery_status='I') | Q(delivery_status='N') | Q(delivery_status='D'), quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, payment_status='P').order_by('-id')
            paginator = Paginator(ordersAllQuerySet, records_per_page)
            page_number = request.GET.get('page')
            context['ordersAllData'] = paginator.get_page(page_number)

            context['records_per_page'] = records_per_page
            context['ordersAllTabCount'] = Order.objects.filter(Q(delivery_status='I') | Q(delivery_status='N') | Q(delivery_status='D'), quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, payment_status='P').count()

#--------------------------------------------------------------------- start language pair and no of files  --------------------------------------------------------------------------------
            # quoteId = Order.objects.filter(quote_price__quote__request__customer=customer,quote_price__quote__request__customer__profile__id=request.user.id, delivery_status='N' or 'I').order_by('-id')
            targetLanguages = RequestTargetLanguage.objects.filter(request__customer=customer).order_by('-id')
            request_items = RequestItem.objects.filter(request__customer=customer,request__customer__profile__id=request.user.id).order_by('-id')
            for order in context['ordersActiveData']:
                    setattr(order,'target_langs',[])
                    setattr(order,'no_of_files',0)
                    for lang in targetLanguages:
                        if(order.quote_price.quote.request.id == lang.request.id):
                            order.target_langs.append(lang)
                    for request_item in request_items:
                        if(order.quote_price.quote.request.id == request_item.request.id):
                            order.no_of_files += 1
                            
            for delivered in context['ordersDeliveredData']:
                    setattr(delivered,'target_langs',[])
                    setattr(delivered,'no_of_files',0)
                    for lang in targetLanguages:
                        if(delivered.quote_price.quote.request.id == lang.request.id):
                            delivered.target_langs.append(lang)
                            # delivered['target_langs'].append(lang)
                    for request_item in request_items:
                        if(delivered.quote_price.quote.request.id == request_item.request.id):
                            delivered.no_of_files += 1

            for allorders in context['ordersAllData']:
                    setattr(allorders,'target_langs',[])
                    setattr(allorders,'no_of_files',0)
                    for lang in targetLanguages:
                        if(allorders.quote_price.quote.request.id == lang.request.id):
                            allorders.target_langs.append(lang)
                    for request_item in request_items:
                        if(allorders.quote_price.quote.request.id == request_item.request.id):
                            allorders.no_of_files += 1
#-------------------------------------------------------------------- end language pair and no of files  ----------------------------------------------------------------------------

#------------------------------------------------------------------ end filter-modal by zulkifal 4/16/23 ----------------------------------------------------------------------------
            filterModal = {}

            if request.method == 'GET':
                ordersActiveQuerySet = Order.objects.filter(quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, delivery_status='N' or 'I').order_by('-id')
                ordersDeliveredQuerySet = Order.objects.filter(quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, delivery_status='D').order_by('-id')
                ordersAllQuerySet = Order.objects.filter(quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id).order_by('-id')
                if request.GET.get('created_at__gte'):
                    filterModal['created_at__gte'] = request.GET.get('created_at__gte')
                if request.GET.get('created_at__lte'):
                    filterModal['created_at__lte'] = request.GET.get('created_at__lte')
                if request.GET.get('workflow'):
                    filterModal['quote_price__workflow__name__icontains'] = request.GET.get('workflow')
                if request.GET.get('lang_from__icontains'):
                    filterModal['quote_price__quote__request__lang_from__name__icontains'] = request.GET.get('lang_from__icontains')
                if request.GET.get('price'):
                    filterModal['quote_price__price'] = request.GET.get('price')
                if request.GET.get('word_count'):
                    filterModal['quote_price__quote__word_count'] = request.GET.get('word_count')
                if filterModal:
                    ordersActiveQuerySet = ordersActiveQuerySet.filter(**filterModal)
                    ordersDeliveredQuerySet = ordersDeliveredQuerySet.filter(**filterModal)
                    ordersAllQuerySet = ordersAllQuerySet.filter(**filterModal)
                    context['ordersActiveData'] = ordersActiveQuerySet
                    context['ordersDeliveredData'] = ordersActiveQuerySet
                    context['ordersAllData'] = ordersActiveQuerySet

                    # quoteId = Order.objects.filter(quote_price__quote__request__customer=customer,quote_price__quote__request__customer__profile__id=request.user.id, delivery_status='N' or 'I').order_by('-id')
                    targetLanguages = RequestTargetLanguage.objects.filter(request__customer=customer).order_by('-id')
                    request_items = RequestItem.objects.filter(request__customer=customer,request__customer__profile__id=request.user.id).order_by('-id')
                    for order in context['ordersActiveData']:
                            setattr(order,'target_langs',[])
                            setattr(order,'no_of_files',0)
                            for lang in targetLanguages:
                                if(order.quote_price.quote.request.id == lang.request.id):
                                    order.target_langs.append(lang)
                            for request_item in request_items:
                                if(order.quote_price.quote.request.id == request_item.request.id):
                                    order.no_of_files += 10

                    for delivered in context['ordersDeliveredData']:
                        setattr(delivered,'target_langs',[])
                        setattr(delivered,'no_of_files',0)
                        for lang in targetLanguages:
                            if(delivered.quote_price.quote.request.id == lang.request.id):
                                delivered.target_langs.append(lang)
                        for request_item in request_items:
                            if(delivered.quote_price.quote.request.id == request_item.request.id):
                                delivered.no_of_files += 1

                    for allorders in context['ordersAllData']:
                            setattr(allorders,'target_langs',[])
                            setattr(allorders,'no_of_files',0)
                            for lang in targetLanguages:
                                if(allorders.quote_price.quote.request.id == lang.request.id):
                                    allorders.target_langs.append(lang)
                            for request_item in request_items:
                                if(allorders.quote_price.quote.request.id == request_item.request.id):
                                    allorders.no_of_files += 1
#------------------------------------------------------------------ end filter-modal by zulkifal 4/16/23 ----------------------------------------------------------------------------

#----------------------------------------------------------------------start search filter by zulkifal ----------------------------------------------------------------------------
            if request.method == 'GET':
                searchFilter = request.GET.get('search')
                ordersActiveData = Order.objects.filter(Q(delivery_status='I') | Q(delivery_status='N'), quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, payment_status='P')
                ordersDeliveredData = Order.objects.filter(quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, delivery_status='D')
                ordersAllData = Order.objects.filter(Q(delivery_status='I') | Q(delivery_status='N') | Q(delivery_status='D'), quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, payment_status='P')
                if searchFilter and searchFilter.isdigit():
                    ordersActiveData = Order.objects.filter(id=searchFilter)
                    ordersDeliveredData = Order.objects.filter(id=searchFilter)
                    ordersAllData = Order.objects.filter(id=searchFilter)
                context['searchFilter'] = searchFilter
                context['ordersActiveData'] = ordersActiveData.order_by('-id')
                context['ordersDeliveredData'] = ordersDeliveredData.order_by('-id')
                context['ordersAllData'] = ordersAllData.order_by('-id')
                if ordersActiveData.exists():
                    targetLanguages = RequestTargetLanguage.objects.filter(request__customer=customer)
                    request_items = RequestItem.objects.filter(request__customer=customer,request__customer__profile__id=request.user.id).order_by('-id')
                    for order in ordersActiveData:
                        order.target_langs = targetLanguages.filter(request__id=order.quote_price.quote.request.id)
                        order.no_of_files = sum([10 for request_item in request_items if request_item.request.id == order.quote_price.quote.request.id])

                if ordersDeliveredData.exists():
                    targetLanguages = RequestTargetLanguage.objects.filter(request__customer=customer)
                    request_items = RequestItem.objects.filter(request__customer=customer,request__customer__profile__id=request.user.id).order_by('-id')
                    for delivered in ordersDeliveredData:
                        delivered.target_langs = targetLanguages.filter(request__id=delivered.quote_price.quote.request.id)
                        delivered.no_of_files = sum([1 for request_item in request_items if request_item.request.id == delivered.quote_price.quote.request.id])

                if ordersAllData.exists():
                    targetLanguages = RequestTargetLanguage.objects.filter(request__customer=customer)
                    request_items = RequestItem.objects.filter(request__customer=customer,request__customer__profile__id=request.user.id).order_by('-id')
                    for allorders in ordersAllData:
                        allorders.target_langs = targetLanguages.filter(request__id=allorders.quote_price.quote.request.id)
                        allorders.no_of_files = sum([1 for request_item in request_items if request_item.request.id == allorders.quote_price.quote.request.id])

#------------------------------------------------------------------------ end search filter by zulkifal ----------------------------------------------------------------------------
            if(context['is_corporate_PC']):
                corporate_users = Customer.objects.filter(customer_company__id= context['corporate_id'])
                context['orders'] = Order.objects.filter(quote_price__quote__request__customer__in=corporate_users).order_by('-id')
                context['requests'] = Request.objects.filter(customer__in=corporate_users).order_by('-id')
                context['invoices'] = Invoice.objects.filter(order__quote_price__quote__request__customer__in=corporate_users).order_by('-id')
                context['payments'] = Payment.objects.filter(order__quote_price__quote__request__customer__in=corporate_users).order_by('-id')
                # for price
                customer = Customer.objects.get(profile=request.user)
                context['owner'] = customer
                if(context['is_corporate_PC']):
                    corporate_users = Customer.objects.filter(customer_company__id= context['corporate_id'])
                    context['orders'] = Order.objects.filter(quote_price__quote__request__customer__in=corporate_users).order_by('-id')
                else:
                    context['orders'] = Order.objects.filter(quote_price__quote__request__customer=customer).order_by('-id')
                session_company = get_session_company(request.session['company_id']) if 'company_id' in request.session else None
                if session_company:
                    company = session_company
                else:
                    company = Company.objects.get(id=1)
                
                context['company'] = company

            else:
                context['orders'] = Order.objects.filter(quote_price__quote__request__customer=customer).order_by('-id')
                context['requests'] = Request.objects.filter(customer=customer).order_by('-id')
                context['invoices'] = Invoice.objects.filter(order__quote_price__quote__request__customer=customer).order_by('-id')
                context['payments'] = Payment.objects.filter(order__quote_price__quote__request__customer=customer).order_by('-id')

            # checking redirect path
            return render(request, self.userTemplate, context)

        else:
            print('admin')

        # filter objects for desired data in orders pending
        # ordersActivePagination = Order.objects.filter(quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, payment_status='P').order_by('-id')
        # context['ordersActivePagination'] = ordersActivePagination


        if request.session.get('user_access_level'):
            if request.session['user_access_level'] == 0:
                self.template = 'pages/content/_customer_content.html'
                context = self.getCustomerContext(request)

            return render(request, self.othersTemplate, context)
        else:
            # return redirect(reverse('dashboard'))
            return render(request, self.othersTemplate, context)

    def getCustomerContext(self, request):
        context = {}
        return context


# orders peending view
class ordersPending(View):
    template = 'pages/ordersPending.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):

        context = {}
        company = get_session_company(request.session['company_id'])
        customer = Customer.objects.get(profile=request.user)
        context['owner'] = customer
        if(customer.customer_company != None):
                customer_company = CustomerCompany.objects.get(id=customer.customer_company.id)
                context['credit_line'] = customer_company.credit_limit + customer_company.credit_note + customer_company.pre_payment
        else:
                context['credit_line']= customer.pre_payment + customer.credit_limit + customer.credit_note

        inProgressCount = Order.objects.filter(quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, payment_status='U' or 'R').order_by('-id').count()  
        context['inProgressCount'] = inProgressCount

        user_type = request.user.profile.user_type
        print(user_type)
        print("profile id",request.user.profile.id);
        corporates = CustomerCompanyPrimaryContact.objects.filter(primary_contact=request.user.profile)
        print(corporates)
        context['is_corporate_PC'] = 0
        if(len(corporates)):
            context['is_corporate_PC'] = 1
            context['corporate_id'] = corporates[0].customer_company.id #Assuming a person can have one corport

        context['white_label_company'] = white_label_company(request)
        context['ordersPage'] = 'active'

        userEmail = request.user.profile.user    
        customerName =  CustomUser.objects.filter(email=request.user.profile.user)
        context['firstName'] = customerName[0].first_name
        context['lastName'] = customerName[0].last_name

        # zulkifal - for project name 
        userId = request.user.profile.user.id
        context['projectName'] = Project.objects.all().order_by('-id')

        # for price
        customer = Customer.objects.get(profile=request.user)
        context['owner'] = customer
        context['orders'] = Order.objects.filter(quote_price__quote__request__customer=customer).order_by('-id')

        session_company = get_session_company(request.session['company_id']) if 'company_id' in request.session else None
        if session_company:
            company = session_company
        else:
            company = Company.objects.get(id=1)
        
        context['company'] = company

        if user_type == 'PM':
            print('project manager')
            # Pass own and avaiable projects
            project_manager = ProjectManager.objects.get(profile=request.user)
            context['owner'] = project_manager
            context['pm_projects'] = Project.objects.filter(order__quote_price__quote__request__company=company).order_by('-id')
            context['pm_languages'] = ProjectManagerLanguage.objects.filter(project_manager=project_manager.id)
            context['pm_work_experience'] = WorkExperience.objects.filter(user=request.user)
        elif user_type == 'AM':
            account_manager = AccountManager.objects.get(profile=request.user)
            context['owner'] = account_manager
        elif user_type == 'VM':
            vendor_manager = VendorManager.objects.get(profile=request.user)
            context['owner'] = vendor_manager
        elif user_type == 'TR':
            print('translator')
            # Pass own jobs and invoices
            translator = Translator.objects.get(profile=request.user)
            context['owner'] = translator
            context['tr_jobs_assignments'] = JobAssignment.objects.filter(translator=translator, is_active=True).order_by('-id')
            context['tr_jobs_invitations'] = JobInvitation.objects.all().order_by('-id')
            context['tr_languages'] = TranslatorLanguage.objects.filter(translator=translator.id)
            context['tr_prices'] = TranslatorPrice.objects.filter(translator=translator.id)
            context['tr_work_experience'] = WorkExperience.objects.filter(user=request.user)
            context['tr_payments'] = TranslatorPayment.objects.filter(translator_order_id__translator=translator)

            if not UserFinancialAccount.objects.filter(user=request.user).exists():
                UserFinancialAccount.objects.create(user=request.user)
            context['tr_account_balance'] = UserFinancialAccount.objects.filter(user=request.user).first().balance
            context['tr_bills'] = TranslatorInvoice.objects.filter(translator_order_id__translator=translator).order_by('-id')
            
        elif user_type == 'CU':
            
            print('Customer')
            # Pass own orders and invoices
            customer = Customer.objects.get(profile=request.user)
            context['owner'] = customer
            context['orders'] = Order.objects.filter(quote_price__quote__request__customer=customer).order_by('-id')

            # in progress count
            context['ordersPendingActiveCount'] = Order.objects.filter(quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, payment_status='U' or 'R').count()
            # zk - dynamic pagination
            records_per_page = int(request.GET.get('records_per_page', 20))
            # for ordersPendingActivePagination
            ordersPendingActiveQuerySet = Order.objects.filter(quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, payment_status='U' or 'R').order_by('-id')
            paginator = Paginator(ordersPendingActiveQuerySet, records_per_page)
            page_number = request.GET.get('page')
            context['ordersPendingActiveData'] = paginator.get_page(page_number)
            context['records_per_page'] = records_per_page

#-------------------------------------------------------------------------- start language pair --------------------------------------------------------------------------------
            targetLanguages = RequestTargetLanguage.objects.filter(request__customer=customer).order_by('-id')
            request_items = RequestItem.objects.filter(request__customer=customer,request__customer__profile__id=request.user.id).order_by('-id')
            
            for order in context['ordersPendingActiveData']:
                    setattr(order,'target_langs',[])
                    setattr(order,'no_of_files',0)
                    for lang in targetLanguages:
                        if(order.quote_price.quote.request.id == lang.request.id):
                            order.target_langs.append(lang)
                    for request_item in request_items:
                        if(order.quote_price.quote.request.id == request_item.request.id):
                            order.no_of_files += 1
#-------------------------------------------------------------------------- end language pair --------------------------------------------------------------------------------

#---------------------------------------------------------------------- start filter-modal by zulkifal 4/16/23 --------------------------------------------------------------------------------
            filterModal = {}

            if request.method == 'GET':
                ordersPendingActiveQuerySet = Order.objects.filter(quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, payment_status='U' or 'R').order_by('-id')
                if request.GET.get('created_at__gte'):
                    filterModal['created_at__gte'] = request.GET.get('created_at__gte')
                if request.GET.get('created_at__lte'):
                    filterModal['created_at__lte'] = request.GET.get('created_at__lte')
                if request.GET.get('workflow'):
                    filterModal['quote_price__workflow__name__icontains'] = request.GET.get('workflow')
                if request.GET.get('lang_from__icontains'):
                    filterModal['quote_price__quote__request__lang_from__name__icontains'] = request.GET.get('lang_from__icontains')
                if request.GET.get('price'):
                    filterModal['quote_price__price'] = request.GET.get('price')
                if request.GET.get('word_count'):
                    filterModal['quote_price__quote__word_count'] = request.GET.get('word_count')
                if filterModal:
                    ordersPendingActiveQuerySet = ordersPendingActiveQuerySet.filter(**filterModal)
                    context['ordersPendingActiveData'] = ordersPendingActiveQuerySet
                    # no of files, language pair 
                    # quoteId = Order.objects.filter(quote_price__quote__request__customer=customer,quote_price__quote__request__customer__profile__id=request.user.id, delivery_status='N' or 'I').order_by('-id')
                    targetLanguages = RequestTargetLanguage.objects.filter(request__customer=customer).order_by('-id')
                    request_items = RequestItem.objects.filter(request__customer=customer,request__customer__profile__id=request.user.id).order_by('-id')
                    for order in context['ordersPendingActiveData']:
                            setattr(order,'target_langs',[])
                            setattr(order,'no_of_files',0)
                            for lang in targetLanguages:
                                if(order.quote_price.quote.request.id == lang.request.id):
                                    order.target_langs.append(lang)
                            for request_item in request_items:
                                if(order.quote_price.quote.request.id == request_item.request.id):
                                    order.no_of_files += 1
#---------------------------------------------------------------------- end filter-modal by zulkifal 4/16/23 --------------------------------------------------------------------------------

#---------------------------------------------------------------------- start search filter by zulkifal -------------------------------------------------------------------------------------
            if request.method == 'GET':
                searchFilter = request.GET.get('search')
                if searchFilter != None:
                    context['searchFilter'] = searchFilter
                    context['ordersPendingActiveData'] = Order.objects.filter(id=searchFilter, quote_price__quote__request__customer=customer, quote_price__quote__request__customer__profile__id=request.user.id, payment_status='U' or 'R').order_by('-id')

                    targetLanguages = RequestTargetLanguage.objects.filter(request__customer=customer).order_by('-id')
                    request_items = RequestItem.objects.filter(request__customer=customer,request__customer__profile__id=request.user.id).order_by('-id')
                    for order in context['ordersPendingActiveData']:
                            setattr(order,'target_langs',[])
                            setattr(order,'no_of_files',0)
                            for lang in targetLanguages:
                                if(order.quote_price.quote.request.id == lang.request.id):
                                    order.target_langs.append(lang)
                            for request_item in request_items:
                                if(order.quote_price.quote.request.id == request_item.request.id):
                                    order.no_of_files += 1
#---------------------------------------------------------------------- end search filter by zulkifal ---------------------------------------------------------------------------------------
            context['requests'] = Request.objects.filter(customer=customer).order_by('-id')
            context['invoices'] = Invoice.objects.filter(order__quote_price__quote__request__customer=customer).order_by('-id')
            context['payments'] = Payment.objects.filter(order__quote_price__quote__request__customer=customer)

        else:
            print('admin')
        
        if request.session.get('user_access_level'):
            if request.session['user_access_level'] == 0:
                self.template = 'pages/content/_customer_content.html'
                context = self.getCustomerContext(request)

            return render(request, self.template, context)
        else:
            # return redirect(reverse('dashboard'))
            return render(request, self.template, context)

    def getCustomerContext(self, request):
        context = {}
        return context


## end orders pending view

class Index(View):
    template = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        context = {
            'white_label_company': white_label_company(request)
        }

        # zk - user
        # if user:
        if request.user.is_authenticated:
            userEmail = request.user.profile.user
            customerName = CustomUser.objects.filter(email=request.user.profile.user)
            firstName = customerName[0].first_name
            print("First Name: ", firstName)
            context['firstName'] = customerName[0].first_name
            context['firstLetter'] = firstName[0]

        return render(request, self.template, context)


def page(request, slug):
    path = request.path
    lang = translation.get_language_from_path(path)

    if request.session.get('lang'):
        lang = request.session['lang']
    else:
        lang = 'en'

    if slug:
        check_page = PagesContent.objects.filter(slug=slug, lang=lang).count()
        if check_page > 1:
            page = PagesContent.objects.filter(slug=slug, lang=lang).first()
        elif check_page > 0:
            page = PagesContent.objects.get(slug=slug, lang=lang)
        else:
            page = get_object_or_404(PagesContent, slug=slug, lang='en')

    # If white lable disable all page because the belong to aaaTranslate platform
    if white_label_company(request):
        return redirect('index')

    context = {
        'page': page,
        'white_label_company': white_label_company(request)
    }

    return render(request, 'pages/page.html', context)


# list of news
def news_index(request):
    news = News.objects.order_by('-post_date')
    paginator = Paginator(news, 5)
    page = request.GET.get('page')
    paged_news = paginator.get_page(page)

    for post in paged_news:
        if post.id:
            comments = NewsComment.objects.order_by('-comment_date').filter(comment_post=post.id)
            post.comments_count = comments.count

    context = {
        'news': paged_news
    }
    return render(request, 'news/index.html', context)


# list of news from category
def news_category(request, cat_id):
    news = News.objects.order_by('-post_date').filter(categories=cat_id)
    paginator = Paginator(news, 5)
    page = request.GET.get('page')
    paged_news = paginator.get_page(page)

    for post in paged_news:
        if post.id:
            comments = NewsComment.objects.order_by('-comment_date').filter(comment_post=post.id, show=True)
            post.comments_count = comments.count

    context = {
        'news': paged_news
    }
    return render(request, 'news/index.html', context)


# single post page
def news_single_post(request, post_id):
    if request.method == 'POST':
        author_name = request.POST['author_name']
        author_email = request.POST['author_email']
        author_site = request.POST['author_site']
        comment_text = request.POST['comment_text']
        comment_post = request.POST['comment_post']

        comment = NewsComment(author_name=author_name, author_email=author_email, author_site=author_site, comment_text=comment_text, comment_post_id=int(comment_post))
        comment.save()
        redirect('/news/' + str(post_id))

    post = get_object_or_404(News, pk=post_id)
    comments = NewsComment.objects.order_by('-comment_date').filter(comment_post=post_id, show=True)

    context = {
        'news': post,
        'comments': comments
    }
    return render(request, 'news/news.html', context)


def search(request):
    template = 'pages/search.html'
    context = {}
    company = get_session_company(request.session['company_id'])
    if request.method == 'GET':
        print('Get')
        return render(request, template, context)

    if request.method == 'POST':
        query = request.POST['keyword']
        category = request.POST['category']

        if not query:
            return render(request, template, context)

        if category == 'Customers' or category == 'Any':
            customers = Customer.objects.filter(company=company)
            context['customers'] = customers.filter(Q(profile__first_name__contains=query) | Q(profile__last_name__contains=query) | Q(profile__email__contains=query)).distinct()

        if category == 'Translators' or category == 'Any':
            context['translators'] = Translator.objects.filter(Q(profile__first_name__contains=query) | Q(profile__last_name__contains=query) | Q(profile__email__contains=query)).distinct()

        if category == 'Project Managers' or category == 'Any':
            pms = ProjectManager.objects.filter(profile__companyuser__company=company)
            context['pms'] = pms.filter(Q(profile__first_name__contains=query) | Q(profile__last_name__contains=query) | Q(profile__email__contains=query)).distinct()

        if category == 'Requests' or category == 'Any':
            requests = Request.objects.filter(company=company)
            context['requests'] = requests.filter(Q(customer__profile__first_name__contains=query) | Q(name__contains=query) | Q(delivery_date__contains=query) | Q(customer__profile__last_name__contains=query) | Q(customer__profile__email__contains=query)).distinct()

        if category == 'Quotes' or category == 'Any':
            quotes = Quote.objects.filter(request__company=company)
            context['quotes'] = quotes.filter(Q(request__customer__profile__first_name__contains=query) | Q(date__contains=query) | Q(quoteprice__price__contains=query) | Q(request__customer__profile__last_name__contains=query) | Q(request__customer__profile__email__contains=query)).distinct()

        if category == 'Orders' or category == 'Any':
            orders = Order.objects.filter(quote_price__quote__request__company=company)
            context['orders'] = orders.filter(Q(quote_price__quote__request__customer__profile__first_name__contains=query) | Q(created_at__contains=query) | Q(quote_price__price__contains=query) | Q(quote_price__quote__request__customer__profile__last_name__contains=query) | Q(quote_price__quote__request__customer__profile__email__contains=query)).distinct()

        if category == 'Projects' or category == 'Any':
            projects = Project.objects.filter(order__quote_price__quote__request__company=company)
            context['projects'] = projects.filter(Q(customer__profile__first_name__contains=query) | Q(customer__profile__last_name__contains=query) | Q(customer__profile__email__contains=query) | Q(name__contains=query) | Q(create_date__contains=query))

        if category == 'Invoices' or category == 'Any':
            invoices = Invoice.objects.filter(order__quote_price__quote__request__company=company)
            context['invoices'] = invoices.filter(Q(order__quote_price__quote__request__customer__profile__first_name__contains=query) | Q(due_date__contains=query) | Q(paid_amount__contains=query) | Q(order__quote_price__quote__request__customer__profile__last_name__contains=query) | Q(order__quote_price__quote__request__customer__profile__email__contains=query)).distinct()

        if category == 'Bills' or category == 'Any':
            bills = TranslatorInvoice.objects.filter(translator_order__job__project__order__quote_price__quote__request__company=company)
            context['bills'] = bills.filter(Q(translator_order__translator__profile__first_name__contains=query) | Q(paid_amount__contains=query) | Q(translator_order__translator__profile__last_name__contains=query) | Q(translator_order__translator__profile__email__contains=query)).distinct()

        context['query'] = query
        context['category'] = category

        return render(request, template, context)


def reports(request):
    template = 'pages/reports.html'
    context = {}
    company = get_session_company(request.session['company_id'])

    date_to = datetime.now()
    date_from = date_to - timedelta(days=7)

    if request.method == 'GET':
        print('------------------------Get')

        try:
            if request.GET['category']:
                print('--------------------have category')
                category = request.GET['category']
            else:
                category = 'Any'
        except Exception as e:
            print("Exception Update balance ==========================")
            print(e)
            print("End of Exception  ==========================")
            category = 'Any'

        try:
            if request.GET['date_from']:
                print('--------------------have date_from')
                date_from = request.GET['date_from']
        except Exception as e:
            print("Exception Update balance ==========================")
            print(e)
            print("End of Exception  ==========================")

        try:
            if request.GET['date_to']:
                print('--------------------have date_to')
                date_to = request.GET['date_to']
        except Exception as e:
            print("Exception Update balance ==========================")
            print(e)
            print("End of Exception  ==========================")

        if category == 'Requests' or category == 'Any':
            context['requests'] = Request.objects.filter(company=company, date__range=[date_from, date_to]).order_by('-id')
            print('requests: ', context['requests'])

        if category == 'Quotes' or category == 'Any':
            context['quotes'] = Quote.objects.filter(request__company=company, date__range=[date_from, date_to]).order_by('-id')

        if category == 'Orders' or category == 'Any':
            context['orders'] = orders = Order.objects.filter(quote_price__quote__request__company=company, created_at__range=[date_from, date_to]).order_by('-id')
            for order in orders:
                order.get_or_create_order_project()
                print('order total cost', order.project.get_jobs_cost())

        if category == 'Jobs' or category == 'Any':
            context['jobs'] = Job.objects.filter(project__order__quote_price__quote__request__company=company, create_date__range=[date_from, date_to]).order_by('-id')
            # test only
            # for job in jobs:
            #     print(job.get_assigned_translator_cost())

        if category == 'Invoices' or category == 'Any':
            context['invoices'] = Invoice.objects.filter(order__quote_price__quote__request__company=company, sent_at__range=[date_from, date_to]).order_by('-id')

        if category == 'Bills' or category == 'Any':
            context['bills'] = TranslatorInvoice.objects.filter(translator_order__job__project__order__quote_price__quote__request__company=company, sent_at__range=[date_from, date_to]).order_by('-id')

        context['query'] = None
        if isinstance(date_from, str):
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
        context['date_from'] = date_from
        if isinstance(date_to, str):
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
        context['date_to'] = date_to
        context['category'] = category

        return render(request, template, context)


# Chat ---------------------------------------------------------------------------------------------
@login_required
def chat(request):
    print('---------------------------------chat is called')
    context = {}
    company = get_session_company(request.session['company_id'])
    user_types = ['AD', 'PM', 'VM', 'AM']
    users = CustomUser.objects.filter(companyuser__company=company, profile__user_type__in=user_types)
    # if we want to add translators
    # translators = CustomUser.objects.filter(profile__user_type='TR')
    # users = users.union(translators)
    context['users'] = users

    user_chats = Chat.objects.filter(users=request.user.id)
    print(user_chats)
    user_chats2 = user_chats.filter(users=5)
    print(user_chats2)
    user_chats2 = user_chats2.first()
    print(user_chats2)
    # if post request save new message and make new notifications, send back html of new message
    if request.method == 'POST':
        if request.POST.get("form_type") == 'new_chat':
            print('new chat called')
            # text = request.POST['message']
            author = request.user.id
            receiver = CustomUser.objects.get(id=request.POST['to_id'])

            # 1- Check if there is a private chat or create new
            # get all chats by sender
            sender_chats = Chat.objects.filter(users=request.user.id)
            print(sender_chats)

            # check if the receiver in any chat or create new
            common_chats = sender_chats.filter(users=receiver.id)
            print(common_chats)
            if common_chats:
                chat = common_chats.first()
            else:
                chat = Chat(name='New Chat')
                chat.save()
                chat.users.add(author, receiver)

            # 2- Create message
            msg = ChatMessage(author_id=request.user.id, text=request.POST['message'], chat_id=chat.id)
            msg.save()

            # 3- Create ChatMessageRead for other receivers
            for msg_receiver in chat.users.all():
                if msg_receiver != msg.author:
                    msg_read = ChatMessageRead(message=msg, user=msg_receiver)
                    msg_read.save()

            if msg.id:
                new_msgs = ChatMessage.objects.order_by('id').filter(chat_id=chat.id, id__gt=chat.last_msg)
                chat.last_msg = msg.id
                chat.save()

            # 4- Redirect to chat page
            chats = Chat.objects.order_by('-last_msg').filter(users=request.user.id)
            context = {
            'chats': chats
                }

            if msg.id:
                new_msgs = ChatMessage.objects.order_by('id').filter(chat_id=chat.id, id__gt=chat.last_msg)
                context = {
                    'chat': {
                            'messages': new_msgs
                        }
                }

                return render(request, 'pages/partials/_message.html', context)
            else:
                return JsonResponse({'error': 'Message not saved'}, safe=False)

            # return render(request, 'pages/chat.html', context)
            # return chat(request)

        elif request.POST.get("form_type") == 'create_chat':
            try:
                print('create_chat called')
                # 1- Create a new chat
                chat = Chat(name='New Chat')
                chat.save()

                # 2- add the users to it
                users_list_ids = request.POST.getlist('users')
                print(users_list_ids)

                author = request.user.id
                chat.users.add(author)
                for user_id in users_list_ids:
                    user = CustomUser.objects.get(id=user_id)
                    chat.users.add(user)

                # 3 - Create message
                msg = ChatMessage(author_id=request.user.id, text=request.POST.get('message'), chat_id=chat.id)
                msg.save()

                # 4 - Create ChatMessageRead for other receivers
                for msg_receiver in chat.users.all():
                    if msg_receiver != msg.author:
                        msg_read = ChatMessageRead(message=msg, user=msg_receiver)
                        msg_read.save()

            except Exception as e:
                print("Exception creating chat ==========================")
                print(e)
                print("End of Exception  ==========================")
            return redirect('chat')

        else:
            # create amessage of an existing chat
            chat = Chat.objects.get(id=request.POST['chat'], users=request.user.id)
            if chat:
                msg = ChatMessage(author_id=request.user.id, text=request.POST['text'], chat_id=chat.id)
                msg.save()
                for chat_users in chat.users.all():
                    if chat_users.id and chat_users.id is not request.user.id:
                        notify = ChatNotifications(user_id=chat_users.id, message_id=msg.id, name= "New message to user ")
                        notify.save()
                if msg.id:
                    new_msgs = ChatMessage.objects.order_by('id').filter(chat_id=chat.id, id__gt=chat.last_msg)
                    chat.last_msg = msg.id
                    chat.save()

                # 3- Create ChatMessageRead for other receivers
                for msg_receiver in chat.users.all():
                    if msg_receiver != msg.author:
                        msg_read = ChatMessageRead(message=msg, user=msg_receiver)
                        msg_read.save()

                    context = {
                        'chat': {
                                'messages': new_msgs
                            }
                    }

                    return render(request, 'pages/partials/_message.html', context)
                else:
                    return JsonResponse({'error': 'Message not saved'}, safe=False)

    # get all chats and messages for current user when page is loading
    chats = Chat.objects.order_by('-last_msg').filter(users=request.user.id)
    if chats:
        if chats.count() == 1:
            chats[0].messages = ChatMessage.objects.order_by('id').filter(chat=chats[0].id)
        else:
            for chat_obj in chats:
                chat_obj.messages = ChatMessage.objects.order_by('id').filter(chat=chat_obj.id)
    context = {
        'chats': chats,
        'users': users
    }
    return render(request, 'pages/chat.html', context)


def chatreload(request):
    print('------------------- chatreload called')
    # mark messages as read if have get request
    if request.method == "GET" and "mark_as_read" in request.GET:
        print('-----------------mark_as_read is called')
        messages = ChatMessage.objects.order_by('id').filter(chat=request.GET["mark_as_read"], is_read=False)
        print('messages', messages.count())
        for msg in messages:
            if msg.author_id is not request.user.id:
                msg.is_read = True
                msg.save()

            notify = ChatNotifications.objects.filter(user_id=request.user.id, message_id=msg.id)
            if notify:
                notify.delete()

            # 3- set ChatMessageRead as read
            # messages_read = ChatMessageRead.objects.filter(user_id=request.user.id, message_id=msg.id)
            for msg_read in ChatMessageRead.objects.filter(user=request.user, message=msg):
                msg_read.is_read = True
                msg_read.save()
                print('========================================== 3- set ChatMessageRead as read is applied')

        print('----------------------------- before return')
        # return redirect('chat')
        # return False  ------------ this one should be changed to redirect or HttpResponse

    # get notification count
    if request.method == "GET" and "get_notify_count" in request.GET:
        print('-----------------get_notify_count is called')

        notify = ChatNotifications.objects.filter(user_id=request.user.id)
        context = {
            'notifications': notify.count(),
        }
        print('---------------------notify.count(),', notify.count())
        return JsonResponse(context)

    # if no get request just check for new messages and update chat
    return_obj = {}
    return_chats = {}
    return_obj_tmp = {}

    # chet for new notifications
    notifications = ChatNotifications.objects.order_by('id').filter(user_id=request.user.id)

    if notifications:
        # if hve notifications for this user get all new messages
        for notify in notifications:
            msg = ChatMessage.objects.get(pk=notify.message_id)

            # save messages in dict as (chat_id = list of messages)
            if msg.chat_id not in return_obj_tmp:
                return_obj_tmp = {msg.chat_id: {'messages':{msg.id: msg}}}
            else:
                return_obj_tmp[msg.chat_id]['messages'].update({msg.id: msg})

        # render html for each message
        for i, chat in return_obj_tmp.items():
            chat_msg = {}
            for j, msgs in chat['messages'].items():
                print(j)
                chat_messages = render_to_string('pages/partials/_message.html', {'message': msgs}, request)
                chat_msg.update({j: chat_messages})
            return_obj.update({i: chat_msg})

    # get user chats
    chats = Chat.objects.order_by('last_msg').filter(users=request.user.id)

    # render html for each chat
    if chats:
        for chat in chats:
            chat_html = render_to_string('pages/partials/_chats.html', {'chat': chat}, request)
            return_chats.update({chat.id: chat_html})

    context = {
        'notifications': notifications.count(),
        'chats': return_chats,
        'messages': return_obj
    }

    return JsonResponse(context)


# Email ---------------------------------------------------------------------------------------------
def test_send_email(request):

    # Find it here http://127.0.0.1:8000/test-send-email
    # we test with first record when context is needed

    template = 'pages/test-send-email.html'
    context = {}
    context['templates'] = temapltes = EmailTemplate.objects.all().order_by('id')

    def render_message_context(template, context):
        t = Template(template.body)
        s = Template(template.subject)
        c = Context(context)
        html_message = t.render(c)
        subject = s.render(c)
        plain_message = strip_tags(html_message)
        return html_message, subject, plain_message

    # put the email you want to test the last one in the list below

    # email 1
    email_template_name = 'Registration'
    email_context = {'user': request.user,
                    'branch': CompanyBranch.objects.filter(company__id=1).first()}

    # email 2
    email_template_name = 'Job_Invitation'
    email_context = {'user': request.user,
                    'branch': CompanyBranch.objects.filter(company__id=1).first(),
                    'job': Job.objects.all().first()}

    # email 3
    email_template_name = 'Job_Assignment'
    email_context = {'user': request.user,
                    'branch': CompanyBranch.objects.filter(company__id=1).first(),
                    'job': Job.objects.all().first()}

    # email 4
    email_template_name = 'Job_Receipt'
    email_context = {'user': request.user,
                    'branch': CompanyBranch.objects.filter(company__id=1).first(),
                    'bill': TranslatorInvoice.objects.all().first,
                    'job': Job.objects.all().first()}

    # email 5
    email_template_name = 'Bill_Settlement'
    email_context = {'user': request.user,
                    'branch': CompanyBranch.objects.filter(company__id=1).first(),
                    'translator_payment': TranslatorPayment.objects.all().first(),
                    'job': Job.objects.all().first()}

    # email 6
    email_template_name = 'Job_delivery_Rejected'
    email_context = {'user': request.user,
                    'branch': CompanyBranch.objects.filter(company__id=1).first(),
                    'job': Job.objects.all().first()}

    # email 7
    email_template_name = 'New_Request_received_PM'
    email_context = {'user': request.user,
                    'branch': CompanyBranch.objects.filter(company__id=1).first(),
                    'request': Request.objects.all().first()}

    # email 8
    email_template_name = 'New_order_received_PM'
    email_context = {'user': request.user,
                    'branch': CompanyBranch.objects.filter(company__id=1).first(),
                    'order': Order.objects.all().first()}

    # email 9
    email_template_name = 'Your_order_received_CU'
    email_context = {'user': request.user,
                    'branch': CompanyBranch.objects.filter(company__id=1).first(),
                    'order': Order.objects.all().first()}

    # email 10
    email_template_name = 'New_quote_CU'
    email_context = {'user': request.user,
                    'branch': CompanyBranch.objects.filter(company__id=1).first(),
                    'quote': Quote.objects.all().first()}

    # email 11
    email_template_name = 'payment has_received_CU'
    email_context = {'user': request.user,
                    'branch': CompanyBranch.objects.filter(company__id=1).first(),
                    'receipt': Payment.objects.all().first()}

    # email 12
    email_template_name = 'order_delivered_CU'
    email_context = {'user': request.user,
                    'branch': CompanyBranch.objects.filter(company__id=1).first(),
                    'order': Order.objects.all().first()}

    # email 13
    email_template_name = 'language_pair_rejected'
    email_context = {'user': request.user,
                    'rejector': request.user,
                    'branch': CompanyBranch.objects.filter(company__id=1).first(),
                    'translator_price': TranslatorPrice.objects.all().first()}

    # email 14
    email_template_name = 'job_is_taken'
    email_context = {'user': request.user,
                    'branch': CompanyBranch.objects.filter(company__id=1).first(),
                    'job': Job.objects.all().first()}

    email_template_1 = EmailTemplate.objects.get(name=email_template_name)
    email_context_1 = email_context
    email_html_1, email_subject_1, email_plain_message_1 = render_message_context(email_template_1, email_context_1)
    context['email_html_1'] = email_html_1
    context['email_subject_1'] = email_subject_1
    context['email_plain_message_1'] = email_plain_message_1

    if request.method == 'GET':
        print('         Get')
        return render(request, template, context)

    if request.method == 'POST':
        print('         POST')
        to = 'kim@eito.pro'

        # 1- get template and context

        # 2- show message on page

        # 3- send test email  ##### later

        # Send email to customer
        try:
            template = EmailTemplate.objects.get(name="New_quote_CU")
            email_to = request_obj.customer.profile.email

            t = Template(template.body)
            s = Template(template.subject)
            c = Context({'user': request_obj.customer.profile,
                        'quote': quote_obj,
                        'pm': request.user})
            html_message = t.render(c)
            subject = s.render(c)
            plain_message = strip_tags(html_message)
            from_email = 'aaaTranslate <noReply@aaatranslate.com>'

            send_mail(
                subject,
                plain_message,
                from_email,
                [email_to],
                fail_silently=False,
                html_message=html_message,
            )
            print('email sent to', email_to)
        except Exception as e:
            print("Exception send email ==========================")
            print(e)
            messages.error(request, "Error. Something went wrong.")
            print("End of Exception  ==========================")
        # End of send email

        return render(request, template, context)
