from django.contrib import admin
from finance.models import Account, Transaction, Budget, Category, WishListItem


admin.site.register(Account)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(Budget)
admin.site.register(WishListItem)
