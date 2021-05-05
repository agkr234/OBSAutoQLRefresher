# OBSAutoQLRefresher

OBSでQuake Live配信中に発生する画面のフリーズの復旧作業をスクリプトを用いて行うものです。

フリーズしたGame Captureを非表示/表示する作業を自動化しただけで根本的に画面フリーズを解決するものではありません。

## 必要なもの
- Open Broadcaster Software
- Python 3.6
  - OBSでは3.6のバージョンしか使えないので注意。
- requirements.txtにあるPythonライブラリ

## 使い方
1. Python 3.6のインストール
    - インストール時に"Add Python 3.6 to PATH"にチェックすることを忘れずに。

2. スクリプトをダウンロードして、OBSの*Scripts*ウィンドウでスクリプトを追加する
    - メニューバーの*Tools* > *Scripts* を開いて、開いたウィンドウの左下にある"+"ボタンから追加する。

3. 必要なPythonライブラリをCUI上(コマンドプロンプトなど)でpipを使ってインストール
    - requirements.txtのあるディレクトリに移動し、`pip install -r requirements.txt`を実行する
      - もし、3.6以外のPythonがインストールされているのならば、`py -3.6 -m pip install -r requirements.txt`を実行する。

4. OBSのScriptsウィンドウにある*Python Install Path*をインストールしたPython 3.6のパスに設定する
    - Windowsでの例だと`C:/Users/ユーザー名/AppData/Local/Programs/Python/Python36`
5. *Steam Community URL*を自分のSteam Community Profile URLに設定する。
    - Steamクライアント上でプロフィールページを開いてコピーしたい場合、ページ上で右クリックして *ページのURLをコピーする* をクリック
    - このリンクを開けばすぐに自分のSteam Community Profile Pageに行けるよ！（Steamクライアントの起動とログインが必要） *steam://url/SteamIDMyProfile* 

6. *Target Source*をQuake LiveをキャプチャしているGame captureに選択すれば出来上がり。

## 設定
- Enable this script [checkbox]
  - なぜか最初からOBSにこれがない

- Steam Community URL [string]
  - あなたのゲーム情報と遊んでいるゲームサーバーのIPアドレスを取得ために使います

- Target Source [select]
  - ゲームサーバーに入る/抜ける時、またはゲームサーバーがマップチェンジした際に更新するGame Captureを選択

- Check Interval (ms) [value]
  - どのぐらいの頻度であなたが遊んでいるゲームサーバーの状態をチェックするかをミリ秒で指定
  - 低い数値になるほど頻繁にチェックするようになるが、ゲームサーバーの負担になるのでお勧めしません
  
- Blink Speed (ms) [value]
  - ゲームサーバーに入る/抜ける、またはサーバーチェンジした際にGame Captureの非表示から表示に切り替わるスピード
  - 極端に低い数値にすると、非表示/表示しても画面が治らないかもしれません
  
- Disable the script when Quake Live is not running [checkbox]
  - Quake Liveをプレイしていない時にスクリプトをオフにする設定
  
- Enable debug logging [checkbox]
  - デバック作業時に役に立つかも
  
  
## 今ある問題
- *ローカルサーバーで遊んでいる時に*画面が治らない
  - Steam Community ProfileのページからQuake Liveでロビーにいる状態とローカルサーバーで遊んでいる状態を見分けられないため
- *サーバーに再接続した際に*画面が治らない
  - スクリプトがSteam Community Profileページで遊んでいるサーバーの情報を検知できないほど早く再接続したため。
