# WriteMarkdownLazily

This is a Python script which using for replacing local image with url and adding title for empty title link.

[中文版点我](http://laobie.github.io/python/2016/04/24/replace-image-file-in-markdown.html)

![](http://ac-QYgvX1CC.clouddn.com/04d2ff5eadd5717d.jpg)

### Usage
1. You need to install `tinify` package:
	
	~~~
	pip install --upgrade tinify
	~~~
	see [TinyPNG – API Reference](https://tinypng.com/developers/reference/python)
	
2. You need to install `leancloud-sdk` package:
	
	~~~
	pip install leancloud-sdk
	~~~
	or
	
	~~~
	easy_install leancloud-sdk
	~~~
	see [LeanCloud Python Doc](https://leancloud.cn/docs/python_guide.html#兼容性)

3. Input your api key in `lzmd.py`:
	
	~~~Python
	TINY_API_KEY = "your_tiny_png_api_key"
	LEAN_CLOUD_API_ID = "your_lean_cloud_app_id"
	LEAN_CLOUD_API_KEY = "your_lean_cloud_api_key"
	~~~
	[get TinyPNG api key](https://tinypng.com/developers)
	
	[get LeanCloud api key & id](https://leancloud.cn/)
	
	
4. Write your Markdown file and reference local image files or empty title link:
	
	~~~
	this is a image 
	![](img/monkey.jpg)
	
	[](http://www.baidu.com)
	~~~

5. Use script:
	
	~~~
	python lzmd.py your.md output.md
	~~~
	
	then all local image files references will be replaced with urls of compressed image files, and add title for empty title link.
	
	~~~
	this is a image 
	![](http://ac-QYgvX1CC.clouddn.com/f7597bfa8d7d5689.jpg)
	
	[百度一下，你就知道](http://www.baidu.com)
	~~~

	
### Credits
[Brucezz](https://github.com/brucezz)
	
### License

	Copyright 2016 Jaeger Chen

	Licensed under the Apache License, Version 2.0 (the "License");	you may not use this file except in compliance with the License.
	You may obtain a copy of the License at
	
		http://www.apache.org/licenses/LICENSE-2.0

	Unless required by applicable law or agreed to in writing, software
	distributed under the License is distributed on an "AS IS" BASIS,
	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	See the License for the specific language governing permissions and
	limitations under the License.

	
	
	 
		


