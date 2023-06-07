from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact
from .forms import ContactForm


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            messages.success(request, 'Your message has been sent!')
            return redirect('contacts:contact_success')
    else:
        form = ContactForm()
    return render(request, 'contacts/contact.html', {'form': form})

def contact_success(request):
    return render(request, 'contacts/contact_success.html')
