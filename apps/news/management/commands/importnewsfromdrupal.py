from django.core.management.base import BaseCommand, CommandError
import urllib.request
import json
import pytz
import datetime
import html
import uuid
from apps.news.models import News, NewsThumbImage, NewsBannerImage
from apps.users.models import User
import apps.common.functions

class Command(BaseCommand):
  host = 'https://www1.slcschools.org'
  req = urllib.request.Request(host + '/rest/districtnewsall')
  resp = urllib.request.urlopen(req)
  districtnewsjson = resp.read().decode('utf8')
  districtnews = json.loads(districtnewsjson)

  webmaster = User.objects.get(username='webmaster@slcschools.org')
  timezone = pytz.timezone('America/Denver')
  timezone = pytz.utc
  for article in districtnews:
    article_uuid = uuid.UUID(article['uuid'])
    title = html.unescape(article['title'])
    body = article['body']
    summary = article['body_1']
    pinned = int(article['field_pin_to_home_page'])
    author_date = datetime.datetime(int(article['created_1']),int(article['created_2']), int(article['created_3']), hour=int(article['created_4']), minute=int(article['created_5']), tzinfo=timezone)
    try:
      news = News.objects.get(uuid=article_uuid)
    except News.DoesNotExist:
      news = News.objects.create(uuid=article_uuid,title=title,body=body,author_date=author_date,deleted=0,create_user=webmaster,update_user=webmaster,published=True)
    news.title=title
    news.body=body
    news.summary=summary
    news.pinned=pinned
    news.author_date=author_date
    news.deleted=False
    news.create_user=webmaster
    news.update_user=webmaster
    news.published=True
    news.save()
    if article['field_article_image'] != '':
      try:
        newsthumbimage = NewsThumbImage.objects.get(news=news)
      except NewsThumbImage.DoesNotExist:
        newsthumbimage = NewsThumbImage.objects.create(uuid=uuid.uuid5(news.uuid, article['field_article_image']), news=news, deleted=0,create_user=webmaster,update_user=webmaster, published=1)
      newsthumbimage.alttext=article['field_article_image_2']
      thumbreq = urllib.request.Request(article['field_article_image_1'])
      thumbresp = urllib.request.urlopen(thumbreq)
      imagedata = thumbresp
      original_file, original_extension = apps.common.functions.findfileext_media(article['field_article_image_1'])
      newsthumbimage.image.save(original_file + original_extension, imagedata)
      newsthumbimage.save()
    bannerids = article['field_district_news_banner'].split('***ITEM_SEPARATOR***')
    bannerurls = article['field_district_news_banner_1'].split('***ITEM_SEPARATOR***')
    banneralts = article['field_district_news_banner_2'].split('***ITEM_SEPARATOR***')
    bannercount = 0
    for banner in bannerids:
      if bannerids[bannercount]:
        try:
          newsbannerimage = NewsBannerImage.objects.get(uuid=uuid.uuid5(news.uuid, bannerids[bannercount]))
        except NewsBannerImage.DoesNotExist:
          newsbannerimage = NewsBannerImage.objects.create(uuid=uuid.uuid5(news.uuid, bannerids[bannercount]), news=news, deleted=0,create_user=webmaster,update_user=webmaster, published=1)
        newsbannerimage.alttext=banneralts[bannercount]
        bannerreq = urllib.request.Request(bannerurls[bannercount])
        bannerresp = urllib.request.urlopen(bannerreq)
        imagedata = bannerresp
        original_file, original_extension = apps.common.functions.findfileext_media(bannerurls[bannercount])
        newsbannerimage.image.save(original_file + original_extension, imagedata)
        newsbannerimage.save()
        bannercount += 1
