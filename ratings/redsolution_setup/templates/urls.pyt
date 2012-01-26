# ---- ratings ----

urlpatterns += patterns('',
    (r'^ratings/', include('ratings.urls')),
)