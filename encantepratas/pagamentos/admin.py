from django.contrib import admin
from .models import Pagamento

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'forma_pagamento', 'valor', 'status', 'data_pagamento']
    list_filter = ['forma_pagamento', 'status']