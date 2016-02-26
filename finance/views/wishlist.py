from django.shortcuts import resolve_url
from django.core.urlresolvers import reverse_lazy
from finance.forms import WishListItemForm
from common.views import ListView, CreateView, UpdateView, DeleteView
from finance.models import WishListItem


class WishListItemListView(ListView):
  model = WishListItem
  template_name = 'finance/wishlist/list.html'

  def get_queryset(self):
    return super().get_queryset().order_by('-priority', 'price')


class WishListItemCreateView(CreateView):
  model = WishListItem
  template_name = 'finance/wishlist/create.html'
  form_class = WishListItemForm
  success_url = reverse_lazy('wishlist-list')

  def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)


class WishListItemUpdateView(UpdateView):
  model = WishListItem
  template_name = 'finance/wishlist/update.html'
  form_class = WishListItemForm

  def get_success_url(self):
    return self.request.POST.get('next')

  def get_initial(self,):
    return {'next': self.request.GET.get('next', resolve_url('wishlist-list'))}


class WishListItemDeleteView(DeleteView):
  model = WishListItem
  template_name = 'finance/wishlist/delete.html'
  success_url = reverse_lazy('wishlist-list')
