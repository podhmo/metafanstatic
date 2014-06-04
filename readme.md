genfa
========================================

genfa is creating fanstatic package from source package of target js library and config file (usually json).
if you want to use genfa, takes two step in below instraction.

- 1. using genfa scan for generationg config file.
- 2. call genfa create for generationg python package.

this is demo example.

we have two library twitter bootstrap and zepto.js.
in default, twitter bootstrap depends on jquery, but we want to use alternative library such as zepto.js.
so, generating bootstrap fanstatic package depends on zepto.js, via genfa.


```
$ cd demo
$ ls
bootstrap	zepto
```

genfa scan creates scaffold file for config file.

```
$ genfa scan bootstrap zepto
INFO:genfa.loading:loading: bootstrap/bower.json
please create config file such as below filename:./zepto.bower.json
{
  "dependencies": [], 
  "version": "", 
  "name": "zepto", 
  "main": [
    "zepto.js"
  ], 
  "bower_directory": "zepto", 
  "description": ""
}
```

target package has bower.json (that is bower-repository) then, automatically use it.
on this case, bootstrap is bower-repository, but zepto.js repository doesn't have bower.json file.
if target package doesn't include bower.json, output message about config layout sample and die.
then, you must create config file on yourself.

```
$ genfa scan bootstrap zepto > zepto.bower.json.original
INFO:genfa.loading:loading: bootstrap/bower.json
please create config file such as below filename:./zepto.bower.json

$ diff -u zepto.bower.json.original zepto.bower.json
diff: zepto.bower.json: No such file or directory
$ diff -u zepto.bower.json.original zepto.bower.json
--- zepto.bower.json.original	2014-06-04 01:58:39.000000000 +0900
+++ zepto.bower.json	2014-06-04 01:05:18.000000000 +0900
@@ -1,9 +1,9 @@
 {
+  "dependencies": [], 
   "version": "", 
   "name": "zepto", 
-  "dependencies": [], 
   "main": [
-    "zepto.js"
+    "dist/zepto.min.js"
   ], 
   "bower_directory": "zepto", 
   "description": ""
```

when "<target name>.bower.json" is exists in current directory,
genfa treats this file as target package's bower.json file.

so, this time, genfa scan is succeed!
after that, you have to craete config file, not depends on zepto.js instead of jquery.
bello output is change's diff of this.

```
$ genfa scan bootstrap zepto > config.json.original
INFO:genfa.loading:loading: bootstrap/bower.json
$ diff -u config.json.original config.json
--- config.json.original	2014-06-04 01:59:23.000000000 +0900
+++ config.json	2014-06-04 01:24:48.000000000 +0900
@@ -1,4 +1,13 @@
 {
+  "zepto": {
+    "main": [
+      "dist/zepto.js"
+    ], 
+    "name": "zepto", 
+    "dependencies": [], 
+    "bower_directory": "zepto", 
+    "version": ""
+  }, 
   "bootstrap": {
     "main": [
       "less/bootstrap.less", 
@@ -9,20 +18,11 @@
       "dist/fonts/glyphicons-halflings-regular.ttf", 
       "dist/fonts/glyphicons-halflings-regular.woff"
     ], 
-    "version": "3.1.1", 
-    "bower_directory": "bootstrap", 
     "name": "bootstrap", 
     "dependencies": {
-      "jquery": ">= 1.9.0"
-    }
-  }, 
-  "zepto": {
-    "main": [
-      "dist/zepto.min.js"
-    ], 
-    "version": "", 
-    "bower_directory": "zepto", 
-    "name": "zepto", 
-    "dependencies": []
+      "zepto": ""
+    }, 
+    "bower_directory": "bootstrap", 
+    "version": "3.1.1"
   }
 }
```

now, you can create package via genfa create command.

```
$ genfa create config.json package
rewrite: +package+ -> meta.js.zepto
watch: d genfa/demo/package/meta.js.zepto/js
watch: f genfa/demo/package/meta.js.zepto/dump.txt.tmpl
watch: f genfa/demo/package/meta.js.zepto/Makefile.tmpl
watch: f genfa/demo/package/meta.js.zepto/MANIFEST.in
watch: f genfa/demo/package/meta.js.zepto/README.rst
watch: f genfa/demo/package/meta.js.zepto/setup.py.tmpl
description (package description)[-]:this is fanstatic package for zepto.js
watch: d genfa/demo/package/meta.js.zepto/js/+pythonname+
rewrite: +pythonname+ -> zepto
watch: f genfa/demo/package/meta.js.zepto/js/__init__.py
watch: d genfa/demo/package/meta.js.zepto/js/+pythonname+/resources
watch: f genfa/demo/package/meta.js.zepto/js/+pythonname+/__init__.py.tmpl
copy file: zepto/dist/zepto.js -> genfa/demo/package/meta.js.zepto/js/zepto/resources/dist/zepto.js
copy file: zepto/dist/zepto.min.js -> genfa/demo/package/meta.js.zepto/js/zepto/resources/dist/zepto.min.js
watch: f genfa/demo/package/meta.js.zepto/js/+pythonname+/test_it.py.tmpl
rewrite: +package+ -> meta.js.zepto
watch: f genfa/demo/package/meta.js.zepto/.gitignore
rewrite: +package+ -> meta.js.bootstrap
watch: d genfa/demo/package/meta.js.bootstrap/js
watch: f genfa/demo/package/meta.js.bootstrap/dump.txt.tmpl
watch: f genfa/demo/package/meta.js.bootstrap/Makefile.tmpl
watch: f genfa/demo/package/meta.js.bootstrap/MANIFEST.in
watch: f genfa/demo/package/meta.js.bootstrap/README.rst
watch: f genfa/demo/package/meta.js.bootstrap/setup.py.tmpl
description (package description)[-]:this is fanstatic package for bootstrap
watch: d genfa/demo/package/meta.js.bootstrap/js/+pythonname+
rewrite: +pythonname+ -> bootstrap
watch: f genfa/demo/package/meta.js.bootstrap/js/__init__.py
watch: d genfa/demo/package/meta.js.bootstrap/js/+pythonname+/resources
watch: f genfa/demo/package/meta.js.bootstrap/js/+pythonname+/__init__.py.tmpl
copy file: bootstrap/less/bootstrap.less -> genfa/demo/package/meta.js.bootstrap/js/bootstrap/resources/less/bootstrap.less
copy file: bootstrap/dist/css/bootstrap.css -> genfa/demo/package/meta.js.bootstrap/js/bootstrap/resources/dist/css/bootstrap.css
copy file: bootstrap/dist/js/bootstrap.js -> genfa/demo/package/meta.js.bootstrap/js/bootstrap/resources/dist/js/bootstrap.js
copy file: bootstrap/dist/js/bootstrap.min.js -> genfa/demo/package/meta.js.bootstrap/js/bootstrap/resources/dist/js/bootstrap.min.js
copy file: bootstrap/dist/fonts/glyphicons-halflings-regular.eot -> genfa/demo/package/meta.js.bootstrap/js/bootstrap/resources/dist/fonts/glyphicons-halflings-regular.eot
copy file: bootstrap/dist/fonts/glyphicons-halflings-regular.svg -> genfa/demo/package/meta.js.bootstrap/js/bootstrap/resources/dist/fonts/glyphicons-halflings-regular.svg
copy file: bootstrap/dist/fonts/glyphicons-halflings-regular.ttf -> genfa/demo/package/meta.js.bootstrap/js/bootstrap/resources/dist/fonts/glyphicons-halflings-regular.ttf
copy file: bootstrap/dist/fonts/glyphicons-halflings-regular.woff -> genfa/demo/package/meta.js.bootstrap/js/bootstrap/resources/dist/fonts/glyphicons-halflings-regular.woff
watch: f genfa/demo/package/meta.js.bootstrap/js/+pythonname+/test_it.py.tmpl
rewrite: +package+ -> meta.js.bootstrap
watch: f genfa/demo/package/meta.js.bootstrap/.gitignore
```

these are generated package.
```
$ ls package/
meta.js.bootstrap       meta.js.zepto
```
