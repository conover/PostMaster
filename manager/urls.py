from django.conf.urls.defaults   import patterns, include, url
from manager.views               import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('manager.views',

	# Emails
	url(r'^emails/$',                      EmailListView.as_view(),    name='manager-emails'),
	url(r'^email/create/$',                EmailCreateView.as_view(),  name='manager-email-create'),
	url(r'^email/(?P<pk>\d+)/update/$',    EmailUpdateView.as_view(),  name='manager-email-update'),
	url(r'^email/(?P<pk>\d+)/instances/$', InstanceListView.as_view(), name='manager-email-instances'),

	# Recipients
	url(r'^recipientgroups/$',                       RecipientGroupListView.as_view(),   name='manager-recipientgroups'),
	url(r'^recipientgroup/create/$',                 RecipientGroupCreateView.as_view(), name='manager-recipientgroup-create'),
	url(r'^recipientgroup/(?P<pk>\d+)/recipients/$', RecipientListView.as_view(),        name='manager-recipientgroup-recipients'),
	url(r'^recipient/(?P<pk>\d+)/$',                 RecipientDetailView.as_view(),      name='manager-recipient'),

	url(r'^$', direct_to_template, kwargs={'template':'manager/instructions.html'}, name='manager-home'),
)
