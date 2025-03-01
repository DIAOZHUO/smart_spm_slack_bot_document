# Slack Botの基本説明

## Botの役割
slackの特定なchannelにて, 以下の機能を実現します. 

- STMのコントローラをリモートします. 具体的に, 
LabviewRemoteManagerを通して, LabviewRemoteManager.RemoteDataTypeに書いてある変数のgetとsetします. 
  
- 自然言語エンジンによる会話機能. (クリスマスなどの時期に実験者の寂しい心を慰めます)

## Slackに投稿するメッセージのタイプ
ユーザーさんがchannelに投稿するメッセージは, <u>会話タイプ</u>のメッセージと<u>リモートコマンドタイプ</u>のメッセージがあります. 
会話タイプは普通に投稿すればいいのですが, リモートコマンドタイプは, 

`command_type@@@variable`

みたいな感じで書きます. 文章に`@@@`が含まれると, リモートコマンドタイプとして処理します. 

## Botのリアクション
slackの特定なchannelにて, botはユーザーさんのメッセージに以下のスタンプをつけます. 

- :eyes: : lineの既読と同じ意味です. 
  もしこのスタンプがつけられていない場合, Botがofflineになっているか, useridがbanされているかの状態になります. 

- :two_hearts: : Botはそのメッセージを会話だと認識して処理しました. 

- :sparkles: : Botはそのメッセージをリモートコマンドだと認識して処理しました. 

- :broken_heart: : Botはそのメッセージをリモートコマンドだと認識して処理したが, エラーが起こりました. 



## リモートコマンド

繰り返しますと, リモートコマンドタイプは, 

`command_type@@@variable`

として, `command_type`と`variable`の２つの部分で構成されています. 
送ってきたメッセージの改行は無視されますので, 一行一行づつ送ってください. 
現在公開できる`command_type`は`get`と`set`の２種類です.　

|  command_type  |  役割  |
| ---- | ---- |
|  get  |  変数を取得します  |
|  set  |  変数を変えます  |
|  file  |  ".pkl"のファイルを送ります  |
|  help  |  使える変数をリストアップします  |

##### 1. Get Command
```
get@@@varname
```


varnameはLabviewRemoteManager.RemoteDataTypeやRemoteDataTypeに対応するクラスのメンバー変数です. 
例えば, 
  
`get@@@PythonScanParam`

はPythonScanParamのクラス内の全てのメンバー変数を返します. PythonScanParamのクラス内Aux2ScanSizeという変数がありますが, 

`get@@@Aux2ScanSize`

はその変数だけ返します. 

##### 2. Set Command
```
set@@@varname=value
set@@@varname=json_str 
```

例えば, 

`set@@@PythonScanParam={"Aux1ScanSize"=256, "Aux2ScanSize"=256}`

`set@@@Aux2ScanSize=256`

みたいなコマンドがあります. <u>まとめたクラス</u>(PythonScanParam, StageConfigure, ScanDataHeader)では, =の後ろはjsonの文字列を与えれば, jsonで指定した変数は変更されます. 
<u>普通の変数</u>では, `var_name=var`みたいな感じで送ります. 

##### 3. File Command
```
file@@@path_to_file
```

`file@@@E:\LabviewProject\Labview-SPMController\python\smart_spm\Datas\001_20220114_test`

みたいに<u>拡張子つけず</u>にファイルパスを指定します. ファイルパスはbotがスキャン終了後画像と一緒に投稿しますので,
それをコピーすればよいでしょう.


##### 4. help Command
```
help@@@
```

これは変数(varname)の一覧を動的に送ってくれます. 
下の変数の一覧表はこのドキュメントを更新しないと変わらないが, 
help commandの表示は常に最新の変数の一覧です.


## 変数の一覧表

LabviewRemoteManager.RemoteDataTypeに含む変数

|  variable_type  |  説明  |
| ---- | ---- |
|  PythonScanParam  |  まとめたクラス  |
|  StageConfigure  |  まとめたクラス  |
|  ScanDataHeader  |  まとめたクラス  |
|  DriftX  |  X方向のドリフト(V/s)  |
|  DriftY  |  Y方向のドリフト(V/s)  |
|  DriftZ  |  Z方向のドリフト(V/s)  |
|  DriftX_ADD  |  増加するX方向のドリフト(V/s)  |
|  DriftY_ADD  |  増加するY方向のドリフト(V/s)  |
|  DriftZ_ADD  |  増加するZ方向のドリフト(V/s)  |
|  ScanEnabled  |  scan開始ボタン  |
|  StageOffset_X_Tube  |  Tube ScannerのX軸offset(V)  |
|  StageOffset_Y_Tube  |  Tube ScannerのY軸offset(V)  |
|  StageOffset_X_HS  |  High Speed ScannerのX軸offset(V)  |
|  StageOffset_Y_HS  |  High Speed ScannerのY軸offset(V)  |
|  Go_Home  |  Unisoku Stage ControllerでZをhome positionに戻す  |


まとめた[クラスに含む変数](https://github.com/DIAOZHUO/SPMUtil/blob/main/SPMUtil/structures/scan_data_format.py)

|  variable_type  |  説明  |
| ---- | ---- |
|  Sample_Bias  |    |
|  Tube_Scanner_Offset_X  |    |
|  Tube_Scanner_Offset_Y  |    |
|  High_Speed_Scanner_Offset_X  |    |
|  High_Speed_Scanner_Offset_Y  |    |
|  Scan_Speed  |    |
|  XY_Scan_Option  |    |
|  Z_Scan_Option  |    |
|  Aux1Pingpong  |    |
|  Aux2Pingpong  |    |
|  ZRotation  |    |
|  Aux1MinVoltage  |    |
|  Aux1MaxVoltage  |    |
|  Aux2MinVoltage  |    |
|  Aux2MaxVoltage  |    |
|  Aux1ScanSize  |    |
|  Aux2ScanSize  |    |
|  Aux1Type  |    |
|  Aux2Type  |    |
|  Xtilt  |    |
|  Ytilt  |    |
|  Applytilt  |    |
|  Date  |    |
|  Time_Start_Scan  |    |
|  Time_End_Scan  |    |
|  Scan_Method  |    |




