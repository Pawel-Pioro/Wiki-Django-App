from random import choice
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django import forms
from markdown2 import Markdown
from . import util

class NewEntry(forms.Form):
    title = forms.CharField(label="Entry Title", widget=forms.TextInput(attrs={'class':'form-control col-md-8 col-lg-8'}))  
    content = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control col-md-8 col-lg-8', 'rows':10}))
    edit = forms.BooleanField(initial=False, widget = forms.HiddenInput(), required=False)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    markdown = Markdown()
    entrySite = util.get_entry(entry)
    if entrySite is not None:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown.convert(entrySite),
            "entryTitle": entry
        })
    else:
        return render(request, "encyclopedia/falseEntry.html", {
            "entryTitle": entry
        })

def search(request):
    value = request.GET.get("q", "")
    if (util.get_entry(value) is not None):
        return redirect(f"/wiki/{value}")
    else:
        stringMatches = []
        for entry in util.list_entries():
            if value.lower() in entry.lower():
                stringMatches.append(entry)
        
        return render(request, "encyclopedia/index.html", {
        "entries": stringMatches,
        "value": value,
        "search": True
        })

def newEntry(request):
    if request.method == "POST":
        form = NewEntry(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if (util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title, bytes(content, 'utf8'))
                return redirect(f"/wiki/{title}")
            else:
                return render(request, "encyclopedia/newEntry.html", {
                    "form": form,
                    "entry": title,
                    "existing": True
                })
        else:
            return render(request, "encyclopedia/newEntry.html", {
                "form": form,
                "existing": False
            })
    else:
        return render(request, "encyclopedia/newEntry.html", {
            "form": NewEntry(),
            "existing": False
        })

def edit(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is not None:
        form = NewEntry()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entryPage
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/newEntry.html", {
            "form": form,
            "entryTitle": form.fields["title"].initial,
            "edit": form.fields["edit"].initial
        })
    else:
        return render(request, "encyclopedia/falseEntry.html", {
            "entryTitle": entry
        })

def random(request):
    allEntries = util.list_entries()
    randomEntry = choice(allEntries)
    return redirect(f"/wiki/{randomEntry}")
