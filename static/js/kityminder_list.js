angular.module("kityminder-list", []).controller("KittyminderListController", function ($scope, $http, $compile) {
    window.scope = $scope
    $scope.is_superuser = false
    $scope.user_group_list = []
    $scope.categories = []
    $scope.category_id = 0
    $scope.mindmap_list = []
    $scope.filter = {}
    $scope.slice_page_num = 10
    $scope.page_num = 1

    $scope.new_group
    $scope.new_category
    $scope.new_title

    $scope.new_group = {}

    $scope.load_group = {}
    $scope.load_category
    $scope.load_title

    $scope.load = function () {
        new Promise(function (resolve, reject) {
            // 获取用户是否属于超级用户
            $http({
                method: "GET",
                url: "/blog/kityminder_list/is_superuser",
            }).then(function (data) {
                data = data.data
                $scope.is_superuser = data.data.is_superuser
                resolve()
            })
        }).then(function () {
            return new Promise(function (resolve, reject) {
                // 获取用户所属组的信息
                $http({
                    method: "GET",
                    url: "/blog/kityminder_list/get_user_groups",
                }).then(function (data) {
                    data = data.data
                    $scope.user_group_list = data.data
                    resolve()
                })
            })
        }).then(function () {
            return new Promise(function (resolve, reject) {
                // 获取模块信息，生成模块按钮
                $http({
                    method: "GET",
                    url: "/blog/kityminder_list/get_categories",
                }).then(function (data) {
                    var html_str = ''
                    $scope.categories = data.data.data
                    for (var category of data.data.data) {
                        html_str += '<button class="btn btn-info btn-lg  kityminder-list-btn" type="button" ng-click="selectCategory(' + category.id + ')">' + category.name + '</button>'
                    }
                    var $html = $compile(html_str)($scope); // 编译
                    $html.appendTo(angular.element('.kityminder-list-btn-group')[0])
                    resolve()
                })
            })
        }).then(function () {
            // 获取map表信息，生成列表
            return new Promise(function (resolve, reject) {
                $http({
                    method: "GET",
                    url: "/blog/kityminder_list/get_mindmaps",
                }).then(function (data) {
                    $scope.mindmap_list = data.data.data
                    generateMapList(0)
                    resolve()
                })
            })
        }).then(function () {
            // 更新新建思维导图时模态框的组信息，这里分三种情况，用户属于普通用户但没有属于分组（这种情况不能新建或载入mindmap）、用户属于普通用户有一个分组、用户属于普通用户有多个分组
            if ($scope.user_group_list.length == 0) {
                angular.element('#mindmap-list-new-button-group').remove()
            } else if ($scope.user_group_list.length == 1) {
                var html_str = '<label class="checkbox-inline">' +
                    '    <input type="checkbox" name="group" id="optionsRadios3" ng-model="new_group[' + $scope.user_group_list[0].id + ']" disabled="true"> ' + $scope.user_group_list[0].name +
                    '</label>'
                $scope.new_group[$scope.user_group_list[0].id] = true
            } else {
                var html_str = '<label class="checkbox-inline">' +
                    '    <input type="checkbox" name="group" id="optionsRadios3" ng-model="new_group[' + $scope.user_group_list[0].id + ']"> ' + $scope.user_group_list[0].name +
                    '</label>'
                for (var i = 1; i < $scope.user_group_list.length; i++) {
                    html_str += '<label class="checkbox-inline">' +
                        '    <input type="checkbox" name="group" id="optionsRadios3" ng-model="new_group[' + $scope.user_group_list[i].id + ']"> ' + $scope.user_group_list[i].name +
                        '</label>'
                }
            }
            var $html = $compile(html_str)($scope); // 编译
            angular.element('#maplist-new-modal-group-radio-div').children().remove()
            $html.appendTo(angular.element('#maplist-new-modal-group-radio-div')[0])

            if ($scope.user_group_list.length == 0) {
                angular.element('#mindmap-list-load-button-group').remove()
            } else if ($scope.user_group_list.length == 1) {
                var html_str = '<label class="checkbox-inline">' +
                    '    <input type="checkbox" name="group" id="optionsRadios3" ng-model="load_group[' + $scope.user_group_list[0].id + ']" disabled="true"> ' + $scope.user_group_list[0].name +
                    '</label>'
                $scope.load_group[$scope.user_group_list[0].id] = true
            } else {
                var html_str = '<label class="checkbox-inline">' +
                    '    <input type="checkbox" name="group" id="optionsRadios3" ng-model="load_group[' + $scope.user_group_list[0].id + ']"> ' + $scope.user_group_list[0].name +
                    '</label>'
                for (var i = 1; i < $scope.user_group_list.length; i++) {
                    html_str += '<label class="checkbox-inline">' +
                        '    <input type="checkbox" name="group" id="optionsRadios3" ng-model="load_group[' + $scope.user_group_list[i].id + ']"> ' + $scope.user_group_list[i].name +
                        '</label>'
                }
            }
            var $html = $compile(html_str)($scope); // 编译
            angular.element('#maplist-load-modal-group-radio-div').children().remove()
            $html.appendTo(angular.element('#maplist-load-modal-group-radio-div')[0])

            //更新新建思维导图时模态框的模块信息
            if ($scope.categories.length == 1) {
                var html_str = '<label class="radio-inline">' +
                    '<input type="radio" name="group" id="optionsRadios3" ng-value=' + $scope.categories[0].id + ' ng-model="new_category" disabled="true" ng-checked="1" > ' + $scope.categories[0].name +
                    '</label>'
                $scope.new_category = $scope.categories[0].id
            } else {
                var html_str = '<label class="radio-inline">' +
                    '<input type="radio" name="category" id="optionsRadios3" ng-value=' + $scope.categories[0].id + ' ng-model="new_category" ng-checked="1" > ' + $scope.categories[0].name +
                    '</label>'
                for (var i = 1; i < $scope.categories.length; i++) {
                    html_str += '<label class="radio-inline">' +
                        '<input type="radio" name="category" id="optionsRadios3" ng-value=' + $scope.categories[i].id + ' ng-model="new_category"> ' + $scope.categories[i].name +
                        '</label>'
                }
                $scope.new_category = $scope.categories[0].id
            }
            $html = $compile(html_str)($scope); // 编译
            angular.element('#maplist-new-modal-category-radio-div').children().remove()
            $html.appendTo(angular.element('#maplist-new-modal-category-radio-div')[0])

            if ($scope.categories.length == 1) {
                var html_str = '<label class="radio-inline">' +
                    '<input type="radio" name="group" id="optionsRadios3" ng-value=' + $scope.categories[0].id + ' ng-model="load_category" disabled="true" ng-checked="1" > ' + $scope.categories[0].name +
                    '</label>'
                $scope.load_category = $scope.categories[0].id
            } else {
                var html_str = '<label class="radio-inline">' +
                    '<input type="radio" name="category" id="optionsRadios3" ng-value=' + $scope.categories[0].id + ' ng-model="load_category" ng-checked="1" > ' + $scope.categories[0].name +
                    '</label>'
                for (var i = 1; i < $scope.categories.length; i++) {
                    html_str += '<label class="radio-inline">' +
                        '<input type="radio" name="category" id="optionsRadios3" ng-value=' + $scope.categories[i].id + ' ng-model="load_category"> ' + $scope.categories[i].name +
                        '</label>'
                }
                $scope.load_category = $scope.categories[0].id
            }
            $html = $compile(html_str)($scope); // 编译
            angular.element('#maplist-load-modal-category-radio-div').children().remove()
            $html.appendTo(angular.element('#maplist-load-modal-category-radio-div')[0])


        }).catch(function(err) {
            console.error(err)
        })
    }



    // 选择模块按钮时重新加载列表
    $scope.selectCategory = function (category_id) {
        $scope.category_id = category_id
        if (category_id == 0) {
            $scope.new_category = $scope.categories[0].id
        } else {
            $scope.new_category = category_id
        }

        $scope.filter = {}
        $scope.slice_page_num = 10
        $('#filter-type select:first').val('请选择')
        $('#filter-content:first select').val('')
        // 更改选中的按钮
        buttons = angular.element('.kityminder-list-btn-group').children()
        for (var class_name of angular.element('.kityminder-list-btn-group').children()[category_id + 1].classList) {
            if (class_name == 'active') return
        }
        for (var i = 1; i < buttons.length; i++) {
            for (var class_name of angular.element('.kityminder-list-btn-group').children()[i].classList) {
                if (class_name == 'active') {
                    var class_name = angular.element('.kityminder-list-btn-group').children()[i].className
                    angular.element('.kityminder-list-btn-group').children()[i].className = class_name.substring(0, class_name.indexOf(' active'))
                }
            }
        }
        angular.element('.kityminder-list-btn-group').children()[category_id + 1].className += ' active'
        // $("p").remove(".italic");
        generateMapList(category_id, 1)
    }

    $scope.searchWithFilter = function () {
        if ($('#filter-type option:selected').val() == "请选择") {
            return
        }
        if ($('#filter-content:first').val() == '') {
            $scope.filter = {}
            generateMapList($scope.category_id, 1)
            return
        }
        if ($('#filter-type option:selected').val() == "标题") {
            $scope.filter = { 'title': $('#filter-content:first').val() }
        } else if ($('#filter-type option:selected').val() == "id") {
            $scope.filter = { 'id': parseInt($('#filter-content:first').val()) }
        } else if($('#filter-type option:selected').val() == "组") {
            $scope.filter = { 'group': $('#filter-content:first').val() }
        }
        generateMapList($scope.category_id, 1)
    }

    $scope.selectPage = function (page_num) {
        generateMapList($scope.category_id, page_num)
    }

    $scope.deleteMap = function (map_id) {
        $http({
            method: "POST",
            url: "/blog/kityminder_list/del_mindmap",
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            transformRequest: function (obj) {
                var str = [];
                for (var p in obj) {
                    str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
                }
                return str.join("&");
            },
            data: {
                'id': map_id
            }
        }).then(function (data) {
            if (data.data.code == 0) {
                $http({
                    method: "GET",
                    url: "/blog/kityminder_list/get_mindmaps",
                }).then(function (data) {
                    $scope.mindmap_list = data.data.data
                    generateMapList($scope.category_id, $scope.page_num)
                })
            } else if (data.data.code == -4) {
                alert('权限不够，删除失败！')
            }
        })
    }

    $scope.editMap = function (map_id) {
        var mindmap
        for (var element of $scope.mindmap_list) {
            if (element.id == map_id) {
                mindmap = element
                break
            }
        }
        html_str = '<input type="text"  id="map-list-edit-input' + map_id + '" style="width:auto" value="' + mindmap.title + '"><button  style="width:auto" ng-click="submitEdit(' + map_id + ')">提交</button>'
        var $html = $compile(html_str)($scope); // 编译
        angular.element('#map-list-title-' + map_id).children().remove()
        $html.appendTo(angular.element('#map-list-title-' + map_id)[0])
        $('#map-list-title-' + map_id + ':first')
    }

    $scope.submitEdit = function (map_id) {
        var mindmap
        var html_str
        for (var element of $scope.mindmap_list) {
            if (element.id == map_id) {
                mindmap = element
                break
            }
        }
        update_title = angular.element('#map-list-edit-input' + map_id + '[ type=\'text\' ]').val()
        if (update_title == mindmap.title) {
            html_str = '<a href="/blog/kityminder?id=' + mindmap.id + '" style="display:block;color:black;white-space: nowrap;overflow: hidden;text-overflow: ellipsis; width:300px">' + mindmap.title + '</a>'
            var $html = $compile(html_str)($scope); // 编译
            angular.element('#map-list-title-' + map_id).children().remove()
            $html.appendTo(angular.element('#map-list-title-' + map_id)[0])
        } else {
            $http({
                method: "POST",
                url: "/blog/kityminder_list/update_mindmap_title",
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                transformRequest: function (obj) {
                    var str = [];
                    for (var p in obj) {
                        str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
                    }
                    return str.join("&");
                },
                data: {
                    'id': map_id,
                    'title': update_title
                }
            }).then(function (data) {
                if (data.data.code == 0) {
                    mindmap.title = update_title
                } else if (data.data.code == -4) {
                    alert('权限不足')
                } else {
                    alert('更新失败')
                }
                html_str = '<a href="/blog/kityminder?id=' + mindmap.id + '" style="display:block;color:black;white-space: nowrap;overflow: hidden;text-overflow: ellipsis; width:300px">' + mindmap.title + '</a>'
                var $html = $compile(html_str)($scope); // 编译
                angular.element('#map-list-title-' + map_id).children().remove()
                $html.appendTo(angular.element('#map-list-title-' + map_id)[0])
            })
        }
    }

    $scope.openNewMapModal = function () {

    }

    $scope.deleteNewModalInfo = function () {
        $('#maplist-new-title:first').val('')
    }

    $scope.deleteLoadModalInfo = function () {
        $('#maplist-load-title:first').val('')
    }

    $scope.newMindmap = function () {
        if ($scope.new_title == undefined || $scope.new_title == '') {
            alert('请输入标题！')
            return
        }

        if ($scope.new_group == {}) {
            alert('请选择组！')
            return
        }
        var group_ids = []
        for (var id in $scope.new_group) {
            if ($scope.new_group[id] == true) {
                group_ids.push(id)
            }
        }
        $http({
            method: "POST",
            url: "/blog/kityminder_list/create_mindmap",
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            transformRequest: function (obj) {
                var str = [];
                for (var p in obj) {
                    str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
                }
                return str.join("&");
            },
            data: {
                'title': $scope.new_title,
                'group_ids': group_ids,
                'category_id': $scope.new_category
            }
        }).then(function (data) {
            if (data.data.code == 0) {
                id = data.data.data.id
                window.location = "/blog/kityminder?id=" + id;
            } else {
                alert('创建思维导图失败，请重试')
            }
        })
    }

    $scope.loadMindmap = function () {
        if ($scope.load_title == undefined || $scope.load_title == '') {
            alert('请输入标题！')
            return
        }

        if ($scope.load_group == {}) {
            alert('请选择组！')
            return
        }

        var file_name = document.querySelector('input[type=file]').files[0].name
        var ex_name = file_name.split('.')[file_name.split('.').length - 1]
        if (ex_name != 'xmind') {
            alert('请选择xmind文件')
        }
        var group_ids = []
        for (var id in $scope.load_group) {
            if ($scope.load_group[id] == true) {
                group_ids.push(id)
            }
        }
        var fd = new FormData();
        var file = document.querySelector('input[type=file]').files[0];
        fd.append('upload_file', file);
        fd.append('title', $scope.load_title)
        fd.append('group_ids', group_ids)
        fd.append('category_id', $scope.load_category)
        var host_name = ''
        if("https:" == document.location.protocol) {
            host_name += "https://"
        } else if("http:" == document.location.protocol) {
            host_name += "http://"
        }
        host_name += location.host
        $http({
            method: 'POST',
            url: "/blog/kityminder_list/load_mindmap?host=" + host_name,
            data: fd,
            headers: { 'Content-Type': undefined },
            transformRequest: angular.identity
        }).success(function (response) {
            if(response.code == 0) {
                id = response.data.id
                window.location = "/blog/kityminder?id=" + id;
            } else {
                alert('创建思维导图失败，请重试')
            }
        })

        // $http({
        //     method: "POST",
        //     url: "/blog/kityminder_list/create_mindmap",
        //     headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        //     transformRequest: function (obj) {
        //         var str = [];
        //         for (var p in obj) {
        //             str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
        //         }
        //         return str.join("&");
        //     },
        //     data: {
        //         'title': $scope.load_title,
        //         'group_ids': group_ids,
        //         'category': $scope.load_category
        //     }
        // }).then(function (data) {
        //     if(data.data.code == 0) {
        //         id = data.data.data.id
        //         window.location="/blog/kityminder?id=" + id;
        //     }
        // })
    }

function generateMapList(category_id, page_num) {
    angular.element('tbody tr').remove()
    angular.element('.pagination').remove()
    var temp_map_list = getFilterList(category_id)
    $scope.page_num = page_num
    if (temp_map_list.length > $scope.slice_page_num) {
        page = parseInt(temp_map_list.length / $scope.slice_page_num)
        if (temp_map_list.length % $scope.slice_page_num != 0) {
            page++
        }
        if (page_num > page || page_num == undefined) {
            $scope.page_num = 1
            temp_map_list = temp_map_list.slice(0, $scope.slice_page_num)
            for (var mindmap of temp_map_list) {
                generateMindmapInfo(mindmap)
            }
            generatePageSelection(page, 1)
        } else {
            temp_map_list = temp_map_list.slice($scope.slice_page_num * (page_num - 1), $scope.slice_page_num * (page_num))
            for (var mindmap of temp_map_list) {
                generateMindmapInfo(mindmap)
            }
            generatePageSelection(page, page_num)
        }
    } else {
        for (var mindmap of temp_map_list) {
            generateMindmapInfo(mindmap)
        }
    }
}

function getFilterList(category_id) {
    var filter = $scope.filter
    temp_map_list = []
    if (category_id != 0) {
        for (var mindmap of $scope.mindmap_list) {
            if (mindmap.category_id == category_id) {
                temp_map_list.push(mindmap)
            }
        }
    } else {
        temp_map_list = $scope.mindmap_list
    }
    filter_list = []
    for (var mindmap of temp_map_list) {
        var flag = true
        for (filter_name in filter) {
            if (filter_name == 'title') {
                if (mindmap.title.toLocaleLowerCase().indexOf(filter[filter_name].toLocaleLowerCase()) == -1) {
                    flag = false
                    break;
                }
            }
            if (filter_name == 'id') {
                if (mindmap.id != filter[filter_name]) {
                    flag = false
                    break;
                }
            }
            if(filter_name == 'group') {
                var flag_group = false
                for(var group of mindmap.groups) {
                    if (group.name.toLocaleLowerCase().indexOf(filter[filter_name].toLocaleLowerCase()) != -1) {
                        flag_group = true
                        break
                    }
                }
                if(flag_group == false) {
                    flag = false
                    break
                }
            }
        }
        if (flag) {
            filter_list.push(mindmap)
        }
    }
    return filter_list
}

function generateMindmapInfo(mindmap) {
    // var create_time = new Date(mindmap.create_time)
    // var year = create_time.getFullYear();
    // var month = (create_time.getMonth() + 1) < 10 ? "0" + (create_time.getMonth() + 1) : create_time.getMonth() + 1
    // var day = create_time.getDay() < 10 ? "0" + create_time.getDay() : create_time.getDay()
    // var hours = create_time.getHours() < 10 ? "0" + create_time.getHours() : create_time.getHours()
    // var minuts = create_time.getMinutes() < 10 ? "0" + create_time.getMinutes() : create_time.getMinutes()
    // var seconds = create_time.getSeconds() < 10 ? "0" + create_time.getSeconds() : create_time.getSeconds()
    // var create_time_str = year + '年' + month + '月' + day + '日' + hours + ':' + minuts + ':' + seconds
    var modify_time = new Date(mindmap.modify_time)
    var year = modify_time.getFullYear();
    var month = (modify_time.getMonth() + 1) < 10 ? "0" + (modify_time.getMonth() + 1) : modify_time.getMonth() + 1
    var day = modify_time.getDate() < 10 ? "0" + modify_time.getDate() : modify_time.getDate()
    var hours = modify_time.getHours() < 10 ? "0" + modify_time.getHours() : modify_time.getHours()
    var minuts = modify_time.getMinutes() < 10 ? "0" + modify_time.getMinutes() : modify_time.getMinutes()
    var seconds = modify_time.getSeconds() < 10 ? "0" + modify_time.getSeconds() : modify_time.getSeconds()
    var modify_time_str = year + '年' + month + '月' + day + '日' + hours + ':' + minuts + ':' + seconds

    var group_str = ''
    if (mindmap.groups.length == 1) {
        group_str = mindmap.groups[0].name
    } else if (mindmap.groups.length > 1) {
        for (var i = 0; i < mindmap.groups.length - 1; i++) {
            group_str += mindmap.groups[i].name + '，'
        }
        group_str += mindmap.groups[mindmap.groups.length - 1].name
    }
    if (mindmap.can_edit == true) {
        var html_str = '<tr id="map-list-' + mindmap.id + '">' +
            '<td>' + mindmap.id + '</td>' +
            '<td id="map-list-title-' + mindmap.id + '" style="width:50px"><a href="/blog/kityminder?id=' + mindmap.id + '" style="display:block;color:black;white-space: nowrap;overflow: hidden;text-overflow: ellipsis; width:300px">' + mindmap.title + '</a></td>' +
            '<td style="width:50px">' + group_str + '</td>' +
            '<td style="width:250px">' + modify_time_str + '</td>' +
            '<td><button type="button" class="btn btn-default btn-sm" ng-click=editMap(' + mindmap.id + ')>\n' +
            '        <span class="glyphicon glyphicon-edit"></span>\n' +
            '</button><button type="button" class="btn btn-default btn-sm" ng-click=deleteMap(' + mindmap.id + ')>\n' +
            '        <span class="glyphicon glyphicon-trash"></span>\n' +
            '</button></td>' +
            '</tr>'
        // var html_str = '<li class="list-group-item">\n' +
        // '    <a href="/blog/kityminder?id=' + mindmap.id + '" style="color:black;">' + mindmap.title + '</a>' +
        // '    <button type="button" class="btn btn-default btn-sm" ng-click=deleteMap(' + mindmap.id + ') style="float:right;">\n' +
        // '        <span class="glyphicon glyphicon-trash"></span>\n' +
        // '    </button>\n' +
        // '    <span style="float:right; color:#999999">最后由' + mindmap.modify_user_name + '于' + modify_time_str + '修改&nbsp;&nbsp;</span>' +
        // '</li>'
        var $html = $compile(html_str)($scope); // 编译
        $html.appendTo(angular.element('tbody')[0])
        // angular.element('.list-group')[0].append(
        //     )
    } else {
        var html_str = '<tr id="map-list-' + mindmap.id + '">' + '<td>' + mindmap.id + '</td>' +
            '<td id="map-list-title-' + mindmap.id + '" style="width:50px"><a href="/blog/kityminder?id=' + mindmap.id + '" style="display:block;color:black;white-space: nowrap;overflow: hidden;text-overflow: ellipsis; width:300px">' + mindmap.title + '</a></td>' +
            '<td style="width:50px">' + group_str + '</td>' +
            '<td style="width:250px">' + modify_time_str + '</td>' +
            '<td></td>' +
            '</tr>'
        var $html = $compile(html_str)($scope); // 编译
        $html.appendTo(angular.element('tbody')[0])
    }
}

function generatePageSelection(page, page_num) {
    var html_str = '<div id="page-selection" style="text-align:center;"><ul class="pagination" style="width:auto;">'
    if (page_num == 1) {
        html_str += '<li><a href="#">&laquo;</a></li>'
    } else {
        html_str += '<li><a href="#" ng-click="selectPage(' + (page_num - 1) + ')">&laquo;</a></li>'
    }
    for (var i = 1; i <= page; i++) {
        if (i == page_num) {
            html_str += '<li class="active"><a href="#">' + i + '</a></li>'
        } else {
            html_str += '<li><a href="#" ng-click="selectPage(' + i + ')">' + i + '</a></li>'
        }
    }
    if (page_num == page) {
        html_str += '<li><a href="#">&raquo;</a></li>'
    } else {
        html_str += '<li><a href="#" ng-click="selectPage(' + (page_num + 1) + ')">&raquo;</a></li>'
    }
    html_str += '</ul></div>'
    var $html = $compile(html_str)($scope); // 编译
    $html.appendTo(angular.element('.col-xs-9')[0])
}
});