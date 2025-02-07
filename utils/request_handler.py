from django.shortcuts import render

def request_handler(request, partial_template, context=None):
    context = context or {}
    
    if request.headers.get('HX-Request') == 'true':
        return render(request, partial_template, context)
    
    # Standard request, embed the partial template into the base template
    context['partial_template'] = partial_template
    return render(request, "base.html", context)
