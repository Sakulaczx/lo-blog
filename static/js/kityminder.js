angular.module('kityminder-xmind', ['kityminderEditor'])
    .config(function (configProvider) {
        var url = window.location.href
        var host = url.substring(0, url.indexOf('/blog'))
        configProvider.set('imageUpload', '/blog/kityminder/upload_image?host=' + host);
    }).config(['$locationProvider', function ($locationProvider) {
        $locationProvider.html5Mode(true);
    }]).controller('MainController', function ($scope, $location, $http) {
        vartemp_json = {}
        var id = -1
        $scope.initEditor = function (editor, minder) {
            window.editor = editor;
            window.minder = minder;
            if ($location.search().id == undefined) {
                alert("返回");
                window.history.back(-1);
            } else {
                try {
                    id = parseInt($location.search().id)
                } catch (error) {
                    alert("url参数有误");
                    window.history.back(-1);
                }
                setMapInfo()
            }

            function setMapInfo() {
                $http({
                    method: "GET",
                    url: "/blog/kityminder/get_map_info",
                    params: {
                        'id': id
                    }
                }).then(function (data) {
                    var json_data = data.data
                    if (json_data.code == 0) {
                        minder.importJson(json_data.data)
                        angular.element('#map-title')[0].textContent = json_data.title
                        $scope.title=json_data.title
                        temp_json = window.minder.exportJson()
                        //如果可以编辑的话，每10秒比对一次，有变动则自动保存
                        if (json_data.can_edit && !json_data.is_locked) {
                            setIntervalTask()
                        } else if(!json_data.can_edit){
                            showUpdateInfo('您没有权限对所做的更改进行保存')
                        } else if(json_data.is_locked){
                            showUpdateInfo('该思维导图正被其他用户编辑，您做的修改将不会同步！')
                        }
                    }
                })
            }

            function setIntervalTask() {
                var interval_auto_save = setInterval(function () {
                    var current_map_json = JSON.stringify(editor.minder.exportJson())

                    if (JSON.stringify(current_map_json) != JSON.stringify(temp_json)) {
                        $http({
                            method: "POST",
                            url: "/blog/kityminder/update_map_info",
                            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                            transformRequest: function (obj) {
                                var str = [];
                                for (var p in obj) {
                                    str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
                                }
                                return str.join("&");
                            },
                            data: {
                                'data': current_map_json,
                                'id': id
                            }
                        }).then(function (data) {
                            if (data.data.code == 0) {
                                temp_json = current_map_json
                                var current_time = new Date()
                                var year = current_time.getFullYear();
                                var month = (current_time.getMonth() + 1) < 10 ? "0" + (current_time.getMonth() + 1) : current_time.getMonth() + 1
                                var day = current_time.getDay() < 10 ? "0" + current_time.getDay() : current_time.getDay()
                                var hours = current_time.getHours() < 10 ? "0" + current_time.getHours() : current_time.getHours()
                                var minuts = current_time.getMinutes() < 10 ? "0" + current_time.getMinutes() : current_time.getMinutes()
                                var seconds = current_time.getSeconds() < 10 ? "0" + current_time.getSeconds() : current_time.getSeconds()
                                var text = '已于' + year + "-" + month + "-" + day + " " + hours + ":" + minuts + ":" + seconds + '自动保存。'
                                showUpdateInfo(text)
                            } else if(data.data.code == -4){
                                showUpdateInfo('您当前的权限已经不能对该map执行修改操作，自动保存取消')
                                window.clearInterval(interval_auto_save)
                            } else {
                                showUpdateInfo('自动保存失败')
                            }
                        });
                    }
                }, 10000)

                var interval_auto_lock = setInterval(function () {
                    $http({
                        method: "GET",
                        url: "/blog/kityminder/update_lock",
                        params: {
                            'id': id
                        }
                    }).then(function (data) {
                        if(data.data.code != 0) {
                            showUpdateInfo('上锁失败')
                        }
                    }) 
                }, 5000)
            }
        };
        function showUpdateInfo(text) {
            angular.element('.alert')[0].textContent = text
            angular.element('.alert')[0].style.visibility = 'visible'
            setTimeout(function () {
                angular.element('.alert')[0].style.visibility = 'hidden'
            }, 3000)
        }
        $scope.saveMap = function () {
            var current_map_json = JSON.stringify(editor.minder.exportJson())
            $http({
                method: "POST",
                url: "/blog/kityminder/update_map_info",
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                transformRequest: function (obj) {
                    var str = [];
                    for (var p in obj) {
                        str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
                    }
                    return str.join("&");
                },
                data: {
                    'data': current_map_json,
                    'id': id
                }
            }).then(function (data) {
                if(data.data.code == 0) {
                    temp_json = current_map_json
                    showUpdateInfo('保存成功！')
                } else if(data.data.code == -4) {
                    showUpdateInfo('权限不足，无法保存！')
                }  else if(data.data.code == -8) {
                    showUpdateInfo('思维导图正被其他用户编辑，无法保存！')
                } else {
                    showUpdateInfo('保存失败！')
                }
                
            });
        }

        $scope.saveFile = function () {
            var current_map_json = JSON.stringify(editor.minder.exportJson())
            function post(URL, PARAMS) {
                var temp_form = document.createElement("form");
                temp_form.action = URL;
                temp_form.target = "_blank";
                temp_form.method = "POST";
                temp_form.style.display = "none";
                for (var x in PARAMS) {
                    var opt = document.createElement("textarea");
                    opt.name = x;
                    opt.value = PARAMS[x];
                    temp_form.appendChild(opt);
                }
                document.body.appendChild(temp_form);
                temp_form.submit();
                return temp_form
            }
            params = {'data': current_map_json, 'title': $scope.title}
            temp_form = post("/blog/kityminder/download_xmind", params)
            setTimeout(function() {
                document.body.removeChild(temp_form)
            }, 1000)
            // $http({
            //     method: "POST",
            //     url: "/blog/kityminder/update_map_info",
            //     headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            //     transformRequest: function (obj) {
            //         var str = [];
            //         for (var p in obj) {
            //             str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
            //         }
            //         return str.join("&");
            //     },
            //     data: {
            //         'data': current_map_json,
            //         'id': id
            //     }
            // }).then(function (data) {
            //     var json_data = data.data
            //     if (json_data.code == -4) {

            //     } else if (json_data.code == 0) {
            //         temp_json = current_map_json
            //         window.open('/blog/kityminder/download_xmind?id=' + id)
            //     }
            // });
        }

    });