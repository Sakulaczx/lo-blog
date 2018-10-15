# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     urls.py  
   Description :  
   Author :       JHao
   date：          2017/4/13
-------------------------------------------------
   Change Activity:
                   2017/4/13: 
-------------------------------------------------
"""
__author__ = 'JHao'

from blog import views
from django.conf.urls import url

urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^archive/$', views.archive, name='archive'),
    url(r'^link/$', views.link, name='link'),
    url(r'^message$', views.message, name='message'),
    url(r'^article/(?P<pk>\d+)/$', views.articles, name='article'),
   # url(r'^getComment/$', views.GetComment, name='get_comment'),
    url(r'^detail/(?P<pk>\d+)/$', views.detail, name='detail'),
    url(r'^detail/(?P<pk>\d+)$', views.detail, name='detail'),
    url(r'^search/$', views.search, name='search'),
    url(r'^tag/(?P<name>.*?)/$', views.tag, name='tag'),
    url(r'^coverage/', views.coverage, name='coverage'),
    url(r'^kityminder/get_map_info$', views.getMapInfo),
    url(r'^kityminder/update_map_info$', views.updateMapInfo),
    url(r'^kityminder/update_lock$', views.updateLock),
    url(r'^kityminder/download_xmind$', views.downloadXMind),
    url(r'^kityminder/upload_image$', views.upLoadImage),
    url(r'^kityminder/get_image$', views.getImage),
    url(r'^kityminder$', views.kityminder),
    url(r'^kityminder_list$', views.kityminderList, name='kityminder_list'), 
    url(r'^kityminder_list/get_categories$', views.getCategories),
    url(r'^kityminder_list/get_mindmaps$', views.getMindmaps),
    url(r'^kityminder_list/del_mindmap$', views.delMindmap),
    url(r'^kityminder_list/update_mindmap_title$', views.updateMindmapTitle),
    url(r'^kityminder_list/get_user_groups$', views.getUserGroups),
    url(r'^kityminder_list/is_superuser$', views.isSuperUser),
    url(r'^kityminder_list/create_mindmap$', views.createMindmap),
    url(r'^kityminder_list/load_mindmap$', views.loadMindmap),
]
