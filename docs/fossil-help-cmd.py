from subprocess import run

cmds=['3-way-merge','ci','help','push','stash','add','clean','hook','rebuild','status','addremove','clone','http','reconstruct','sync','alerts','close','import','redo','tag','all','co','info','remote','tarball','amend','commit','init','remote-url','ticket','annotate','configuration','interwiki','rename','timeline','artifact','dbstat','json','reparent','tls-config','attachment','deconstruct','leaves','revert','touch','backoffice','delete','login-group','rm','ui','backup','descendants','ls','rss','undo','bisect','diff','md5sum','scrub','unpublished','blame','export','merge','search','unset','branch','extras','mv','server','unversioned','bundle','finfo','new','settings','update','cache','forget','open','sha1sum','user','cat','fts-config','pikchr','sha3sum','uv','cgi','gdiff','praise','shell','version','changes','git','publish','sql','whatis','chat','grep','pull','sqlar','wiki','checkout','hash-policy','purge','sqlite3','zip']

with open('fossile-cmds-help.org','w') as f:
  for c in cmds:
    d = run(['/home/osboxes/src/fossil-snapshot-20210429/fossil','help',c], capture_output=True)
    f.write(d.stdout.decode('utf-8'))
