from django import forms
from .models import Budget, Transaction, Sponsorship, Investment, Product, Order


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        exclude = ["created_by"]
        widgets = {
            "season":   forms.Select(attrs={"class": "form-select"}),
            "team":     forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "name":     forms.TextInput(attrs={"class": "form-input"}),
            "amount":   forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "notes":    forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ["created_by"]
        widgets = {
            "title":            forms.TextInput(attrs={"class": "form-input"}),
            "transaction_type": forms.Select(attrs={"class": "form-select"}),
            "amount":           forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "date":             forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "category":         forms.Select(attrs={"class": "form-select"}),
            "budget":           forms.Select(attrs={"class": "form-select"}),
            "team":             forms.Select(attrs={"class": "form-select"}),
            "status":           forms.Select(attrs={"class": "form-select"}),
            "reference":        forms.TextInput(attrs={"class": "form-input"}),
            "notes":            forms.Textarea(attrs={"class": "form-input", "rows": 2}),
            "receipt":          forms.FileInput(attrs={"class": "form-input"}),
        }


class SponsorshipForm(forms.ModelForm):
    class Meta:
        model = Sponsorship
        exclude = ["club"]
        widgets = {
            "company_name":  forms.TextInput(attrs={"class": "form-input"}),
            "logo":          forms.FileInput(attrs={"class": "form-input"}),
            "sponsor_type":  forms.Select(attrs={"class": "form-select"}),
            "amount":        forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "currency":      forms.TextInput(attrs={"class": "form-input"}),
            "start_date":    forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "end_date":      forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "status":        forms.Select(attrs={"class": "form-select"}),
            "contact_name":  forms.TextInput(attrs={"class": "form-input"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-input"}),
            "contact_phone": forms.TextInput(attrs={"class": "form-input"}),
            "website":       forms.URLInput(attrs={"class": "form-input"}),
            "contract_file": forms.FileInput(attrs={"class": "form-input"}),
            "notes":         forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }


class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        exclude = ["club"]
        widgets = {
            "investor_name":      forms.TextInput(attrs={"class": "form-input"}),
            "investor_type":      forms.Select(attrs={"class": "form-select"}),
            "amount":             forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "date":               forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "equity_percentage":  forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "notes":              forms.Textarea(attrs={"class": "form-input", "rows": 2}),
            "contact_email":      forms.EmailInput(attrs={"class": "form-input"}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "name":        forms.TextInput(attrs={"class": "form-input"}),
            "slug":        forms.TextInput(attrs={"class": "form-input"}),
            "category":    forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "price":       forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "stock":       forms.NumberInput(attrs={"class": "form-input"}),
            "image":       forms.FileInput(attrs={"class": "form-input"}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["shipping_address", "notes"]
        widgets = {
            "shipping_address": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "notes":            forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }
