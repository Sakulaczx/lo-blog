# -*- coding:utf-8 -*-
import xmind
from xmind.core.markerref import MarkerId
from xmind.core.topic import TopicElement
import json
import random
import string
import os
import time
import xml.etree.ElementTree as ET
import zipfile
import shutil
from blog.models import MindMapImage


def generateRandomString(length):
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(length):
        sa.append(random.choice(seed))
        salt = ''.join(sa)
    return salt


def deleteDir(fileDir, delta_time):
    for eachFile in os.listdir(fileDir):
        if os.path.isfile(fileDir+"/"+eachFile):  # 如果是文件，判断最后修改时间，符合条件进行删除
            ft = os.stat(fileDir+"/"+eachFile)
            ltime = int(ft.st_mtime)  # 获取文件最后修改时间
            #print "文件"+path+"/"+eachFile+"的最后修改时间为"+str(ltime);
            ntime = int(time.time())-delta_time  # 获取现在时间减去deltatime
            if ltime <= ntime:
                os.remove(fileDir+"/"+eachFile)  # 删除3小时前的文件

        elif os.path.isdir(fileDir+"/"+eachFile):  # 如果是文件夹，继续递归
            deleteDir(fileDir+"/"+eachFile, delta_time)


def xmindToJson(path, img_ex_url):
    workbook = xmind.load(path)
    primary_sheet = workbook.getPrimarySheet()  # 得到主画布
    [filename,fename]=os.path.splitext(path)
    [dirname,filename]=os.path.split(path)
    print 'path', path
    temp_dict = {
        "root": {},
        "template": "default",
        "theme": "fresh-blue",
        "version": "1.4.43"
    }
    root = primary_sheet.getRootTopic()
    azip = zipfile.ZipFile(path)
    azip.extractall(dirname + '/' + filename[0:filename.find('.xmind')])
    style_dict = {}
    img_list = []
    xmind_path = ''
    if os.path.exists(dirname + '/' + filename[0:filename.find('.xmind')] + '/styles.xml'):
        xml_style_object = ET.parse(dirname + '/' + filename[0:filename.find('.xmind')] + '/styles.xml')
        for element in xml_style_object.getroot().getchildren():
            tag = element.tag
            if tag.find('}') != -1:
                tag = tag[tag.find('}') + 1:]
            if tag == 'styles':
                styles = element
                break
        for style in styles.getchildren():
            style_id = style.attrib.get('id')
            temp_style_dict = {}
            for (attribute_name, value) in style.getchildren()[0].attrib.items():
                attribute_name = attribute_name[attribute_name.find('}') + 1:]
                if attribute_name == 'font-size':
                    temp_style_dict[attribute_name] = int(value[0:value.find('pt')])
                else:
                    temp_style_dict[attribute_name] = value
            style_dict[style_id] = temp_style_dict
    xmind_path = dirname + '/' + filename[0:filename.find('.xmind')]

    setDict(temp_dict["root"], root, style_dict, img_list, xmind_path, img_ex_url)
    shutil.rmtree(dirname + '/' + filename[0:filename.find('.xmind')])
    kity_minder_json = json.dumps(temp_dict)
    return kity_minder_json, img_list


def jsonToXmind(kity_minder_json, export_path):
    # try:
    dict = json.loads(kity_minder_json)
    # load an existing file or create a new workbook if nothing is found
    workbook = xmind.load(export_path)
    workbook.createSheet()
    primary_sheet = workbook.getPrimarySheet()
    primary_sheet.setTitle("画布1")  # set its title

    root = primary_sheet.getRootTopic()  # get the root topic of this sheet
    setXMindTopic(dict['root'], root)
    xmind.save(workbook, export_path)
    # except Exception as error:
    #     print error
    #     return None


def setDict(dict, topic, style_dict, img_list, xmind_path, img_ex_url):
    dict['data'] = {}
    dict['children'] = []
    # 设置topic的标题
    dict['data']['text'] = topic.getTitle()
    dict['data']['id'] = topic.getID()
    dict['data']['created'] = long(topic.getAttribute('timestamp'))
    dict['data']['hyperlink'] = topic.getHyperlink()
    if topic.getNotes() != None:
        dict['data']['note'] = topic.getNotes().getContent()

    markers = topic.getMarkers()
    if markers != None:
        for marker in markers:
            marker_id = marker.getMarkerId()
            if str(marker_id) == str(MarkerId.priority1):
                dict['data']['priority'] = 1
            elif str(marker_id) == str(MarkerId.priority2):
                dict['data']['priority'] = 2
            elif str(marker_id) == str(MarkerId.priority3):
                dict['data']['priority'] = 3
            elif str(marker_id) == str(MarkerId.priority4):
                dict['data']['priority'] = 4
            elif str(marker_id) == str(MarkerId.priority5):
                dict['data']['priority'] = 5
            elif str(marker_id) == str(MarkerId.priority6):
                dict['data']['priority'] = 6
            elif str(marker_id) == str(MarkerId.priority7):
                dict['data']['priority'] = 7
            elif str(marker_id) == str(MarkerId.priority8):
                dict['data']['priority'] = 8
            elif str(marker_id) == str(MarkerId.priority9):
                dict['data']['priority'] = 9
            elif str(marker_id) == str(MarkerId.task0_8):
                dict['data']['progress'] = 1
            elif str(marker_id) == str(MarkerId.task1_8):
                dict['data']['progress'] = 2
            elif str(marker_id) == str(MarkerId.task2_8):
                dict['data']['progress'] = 3
            elif str(marker_id) == str(MarkerId.task3_8):
                dict['data']['progress'] = 4
            elif str(marker_id) == str(MarkerId.task4_8):
                dict['data']['progress'] = 5
            elif str(marker_id) == str(MarkerId.task5_8):
                dict['data']['progress'] = 6
            elif str(marker_id) == str(MarkerId.task6_8):
                dict['data']['progress'] = 7
            elif str(marker_id) == str(MarkerId.task7_8):
                dict['data']['progress'] = 8
            elif str(marker_id) == str(MarkerId.task8_8):
                dict['data']['progress'] = 9

    style_id = topic.getAttribute('style-id')
    if style_id != None and style_dict.get(style_id) != None:
        style = style_dict[style_id]
        for [style_name, style_value] in style.items():
            if style_name == 'color':
                dict['data']['color'] = style_value #字体颜色
            elif style_name == 'fill':
                dict['data']['background'] = style_value #结点背景色
            elif style_name == 'font-size':
                dict['data']['font-size'] = style_value #字号
            elif style_name == 'font-weight' and style_value == 'bold':
                dict['data']['font-weight'] = style_value #粗体
            elif style_name == 'font-style' and style_value == 'italic':
                dict['data']['font-style'] = style_value #斜体
            elif style_name == 'font-family':
                if style_value == '宋体':
                    dict['data']['font-family'] = '宋体,SimSun'
                elif style_value == '楷体':
                    dict['data']['font-family'] = '楷体,楷体_GB2312,SimKai'
                elif style_value == '黑体':
                    dict['data']['font-family'] = '黑体, SimHei'
                elif style_value == '隶书':
                    dict['data']['font-family'] = '隶书, SimLi'
                elif style_value == 'Arial':
                    dict['data']['font-family'] = 'arial,helvetica,sans-serif'
                elif style_value == 'Arial Black':
                    dict['data']['font-family'] = 'arial black,avant garde'
                elif style_value == 'Comic Sans MS':
                    dict['data']['font-family'] = 'comic sans ms'
                elif style_value == 'Impact':
                    dict['data']['font-family'] = 'impact,chicago'
                elif style_value == 'Times New Roman':
                    dict['data']['font-family'] = 'times new roman'

    img_node = topic.getFirstChildNodeByTagName('xhtml:img')        
    if img_node != None:
        src = img_node.getAttribute('xhtml:src')
        width = img_node.getAttribute('svg:width')
        height = img_node.getAttribute('svg:height')
        if src != None:
            # print 'src', src
            # print 'width', width
            # print 'height', height
            # print xmind_path + src[src.find('xap:') + 4:]
            img_file_path = xmind_path + '/' + src[src.find('xap:') + 4:]
            # print 'img_file_path', img_file_path
            # print 'exist', os.path.exists(img_file_path)
            if os.path.exists(img_file_path):
                [temp_file_path, temp_exname] = os.path.splitext(img_file_path)
                new_img_name = generateRandomString(20) + temp_exname
                shutil.copyfile(img_file_path,os.getcwd() + '/static/map_images/' + new_img_name)
                mindmapimage_object = MindMapImage()
                mindmapimage_object.filename = new_img_name
                mindmapimage_object.save()
                img_list.append(mindmapimage_object.id)
                dict['data']['image'] = img_ex_url + str(mindmapimage_object.id)
                print 'image', dict['data']['image']
                dict['data']['imageTitle'] = None
                if width !=None and height != None:
                    dict['data']['imageSize'] = {
                        'width': width,
                        'height': height
                    }

    sub_topics = topic.getSubTopics()
    if sub_topics != None:
        for sub_topic in sub_topics:
            temp_dict = {}
            setDict(temp_dict, sub_topic, style_dict, img_list, xmind_path, img_ex_url)
            dict['children'].append(temp_dict)
    pass


def setXMindTopic(dict, topic):
    if dict['data'].get('text'):
        topic.setTitle(dict['data'].get('text').encode(
            encoding='UTF-8', errors='strict'))
    if dict['data'].get('created'):
        topic.setModifiedTime(dict['data'].get('created'))
    if dict['data'].get('hyperlink'):
        topic._set_hyperlink(dict['data'].get('hyperlink'))
    if dict['data'].get('note'):
        topic.setPlainNotes(dict['data'].get('note'))
    if dict['data'].get('priority'):
        priority = dict['data'].get('priority')
        if priority == 1:
            topic.addMarker(MarkerId.priority1)
        if priority == 2:
            topic.addMarker(MarkerId.priority2)
        if priority == 3:
            topic.addMarker(MarkerId.priority3)
        if priority == 4:
            topic.addMarker(MarkerId.priority4)
        if priority == 5:
            topic.addMarker(MarkerId.priority5)
        if priority == 6:
            topic.addMarker(MarkerId.priority6)
        if priority == 7:
            topic.addMarker(MarkerId.priority7)
        if priority == 8:
            topic.addMarker(MarkerId.priority8)
        if priority == 9:
            topic.addMarker(MarkerId.priority9)

    if dict['data'].get('progress'):
        progress = dict['data'].get('progress')
        if progress == 1:
            topic.addMarker(MarkerId.task0_8)
        if progress == 2:
            topic.addMarker(MarkerId.task1_8)
        if progress == 3:
            topic.addMarker(MarkerId.task2_8)
        if progress == 4:
            topic.addMarker(MarkerId.task3_8)
        if progress == 5:
            topic.addMarker(MarkerId.task4_8)
        if progress == 6:
            topic.addMarker(MarkerId.task5_8)
        if progress == 7:
            topic.addMarker(MarkerId.task6_8)
        if progress == 8:
            topic.addMarker(MarkerId.task7_8)
        if progress == 9:
            topic.addMarker(MarkerId.task8_8)

    for child_dict in dict['children']:
        topic_element = TopicElement()
        setXMindTopic(child_dict, topic_element)
        topic.addSubTopic(topic_element)


# json_to_xmind(open('data.json').read(), '2.xmind')
# xmind_to_json('CheckList.xmind')
