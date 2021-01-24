// パラメータ取得
var args = WScript.arguments;
var fso  = new ActiveXObject("Scripting.FileSystemObject");

// パラメータ存在チェック
if (args.length > 0) {
  // パラメータ数分ループ
  for (var i = 0; i < args.length; i++) {   
    // パラメータ抽出（ドラッグ＆ドロップしたファイルパス）
    var file = args.item(i);

    // ファイルのフルパス取得
    var fullpath   = fso.GetAbsolutePathName(file);
    var parentpath = fso.GetParentFolderName(fullpath);
    parentpath     = fso.BuildPath(parentpath, "old");

    // フォルダ作成
    if (fso.FolderExists(parentpath)==false) {
      fso.CreateFolder(parentpath);
    }

    // ファイル存在チェック
    if (fso.FileExists(file)) {

      // 拡張子取得
      var ext = fso.GetExtensionName(file).toLowerCase();

      //ファイル名編集
      var FileName, FileBase;
      FileBase = fso.GetBaseName(file);
      FileName = FileBase+"-" + YYYYMMDD() + "."+ext;

      //ファイルコピー(重複処理あり)
      var Modify = 0;
      while(fso.FileExists(fso.BuildPath(parentpath ,FileName))){
        Modify++;
        FileName = FileBase+"-" + YYYYMMDD()+"-"+Modify+"."+ext;
      }
      fso.CopyFile(file,fso.BuildPath(parentpath,FileName));

    } // ファイル存在チェック終了
  }   // for文終了
} else {
  // パラメータが無い場合
  WScript.Echo("ファイルをドラッグ＆ドロップしてください。");
  WScript.Quit(0);
}

// 終了
//WScript.Echo("アーカイブ完了" );
WScript.Quit(0);

function YYYYMMDD() {
  var s = "";
  var d = new Date();
  s += d.getFullYear();
  s += ("0" + (d.getMonth() + 1)).replace(/^\d*(\d{2})$/,"$1");
  s += ("0" + d.getDate()).replace(/^\d*(\d{2})$/,"$1");
  return s;
}
