import requests
import json
import os,subprocess

def get_minecraft_token(YGGDRASIL_API,username: str, password: str):
    """
    通过 Yggdrasil 外置登录接口，使用账号密码获取 Minecraft 登录 Token
    :param username: 用户名/邮箱
    :param password: 密码
    :return: 包含 token、uuid、name 的字典
    """
    # ===================== 配置区（你只需要改这个地址） =====================
    # 这里填你的皮肤站 Yggdrasil 接口，例如 LittleSkin、自建皮肤站
    # ====================================================================

    # 标准 Yggdrasil 认证接口地址
    auth_url = f"{YGGDRASIL_API}/authserver/authenticate"

    # 构造请求体（和 authlib 完全一致）
    payload = {
        "username": username,
        "password": password,
        "clientToken": "python-minecraft-auth-client",  # 自定义客户端标识
        "requestUser": True
    }

    # 请求头
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "MinecraftAuthPython/1.0"
    }

    try:
        # 发送 POST 请求
        response = requests.post(auth_url, data=json.dumps(payload), headers=headers,verify=False)
        response.raise_for_status()  # 抛出 HTTP 错误
        result = response.json()
        print(result)
        # 提取关键信息
        access_token = result.get("accessToken")
        client_token = result.get("clientToken")
        profiles = result.get("availableProfiles", [])

        if not profiles:
            raise Exception("该账号没有创建 Minecraft 角色")

        # 获取角色信息
        profile = profiles[0]
        player_uuid = profile.get("id")
        player_name = profile.get("name")

        # 返回结果
        return {
            "success": True,
            "accessToken": access_token,
            "clientToken": client_token,
            "playerUUID": player_uuid,
            "playerName": player_name,
            "rawResponse": result
        }

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"请求失败：{str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    try:
        os.chdir('mcbxb')
    except:pass
    jarPath = r".minecraft\libraries\authlib-injector.jar"

    YGGDRASIL_API_INPUT = input("请输入YGGDRASIL_API，示例：https://littleskin.cn/api/yggdrasil，留空则为MXHA：")
    YGGDRASIL_API = "https://mxha.barrierslink.cn/api/yggdrasil"
    if YGGDRASIL_API_INPUT:
        YGGDRASIL_API = YGGDRASIL_API_INPUT
    username = input("请输入用户名/邮箱：")
    password = input("请输入密码：")
    print("\n正在登录验证...")
    token_data = get_minecraft_token(YGGDRASIL_API,username, password)
    
    if token_data["success"]:
        # print(f"{token_data['accessToken']}")
        subprocess.run(r'''"java\bin\java.exe" -Dstderr.encoding=UTF-8 -Dstdout.encoding=UTF-8 -Dfile.encoding=COMPAT -XX:+UseG1GC -XX:-UseAdaptiveSizePolicy -XX:-OmitStackTraceInFastThrow -Djdk.lang.Process.allowAmbiguousCommands=true -Dfml.ignoreInvalidMinecraftCertificates=True -Dfml.ignorePatchDiscrepancies=True -Dlog4j2.formatMsgNoLookups=true -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump "-Djava.library.path=.minecraft\versions\1.21.11-Quilt\1.21.11-Quilt-natives" "-Djna.tmpdir=.minecraft\versions\1.21.11-Quilt\1.21.11-Quilt-natives" "-Dorg.lwjgl.system.SharedLibraryExtractPath=.minecraft\versions\1.21.11-Quilt\1.21.11-Quilt-natives" "-Dio.netty.native.workdir=.minecraft\versions\1.21.11-Quilt\1.21.11-Quilt-natives" -Dminecraft.launcher.brand=PCL -Dminecraft.launcher.version=369 -cp ".minecraft\libraries\net\fabricmc\sponge-mixin\0.16.5+mixin.0.8.7\sponge-mixin-0.16.5+mixin.0.8.7.jar;.minecraft\libraries\org\quiltmc\quilt-json5\1.0.4+final\quilt-json5-1.0.4+final.jar;.minecraft\libraries\org\ow2\asm\asm\9.9\asm-9.9.jar;.minecraft\libraries\org\ow2\asm\asm-analysis\9.9\asm-analysis-9.9.jar;.minecraft\libraries\org\ow2\asm\asm-commons\9.9\asm-commons-9.9.jar;.minecraft\libraries\org\ow2\asm\asm-tree\9.9\asm-tree-9.9.jar;.minecraft\libraries\org\ow2\asm\asm-util\9.9\asm-util-9.9.jar;.minecraft\libraries\org\quiltmc\quilt-config\1.3.3\quilt-config-1.3.3.jar;.minecraft\libraries\net\fabricmc\intermediary\1.21.11\intermediary-1.21.11.jar;.minecraft\libraries\org\quiltmc\quilt-loader\0.30.0-beta.0\quilt-loader-0.30.0-beta.0.jar;.minecraft\libraries\at\yawk\lz4\lz4-java\1.8.1\lz4-java-1.8.1.jar;.minecraft\libraries\com\azure\azure-json\1.4.0\azure-json-1.4.0.jar;.minecraft\libraries\com\github\oshi\oshi-core\6.9.0\oshi-core-6.9.0.jar;.minecraft\libraries\com\google\code\gson\gson\2.13.2\gson-2.13.2.jar;.minecraft\libraries\com\google\guava\failureaccess\1.0.3\failureaccess-1.0.3.jar;.minecraft\libraries\com\google\guava\guava\33.5.0-jre\guava-33.5.0-jre.jar;.minecraft\libraries\com\ibm\icu\icu4j\77.1\icu4j-77.1.jar;.minecraft\libraries\com\microsoft\azure\msal4j\1.23.1\msal4j-1.23.1.jar;.minecraft\libraries\com\mojang\authlib\7.0.61\authlib-7.0.61.jar;.minecraft\libraries\com\mojang\blocklist\1.0.10\blocklist-1.0.10.jar;.minecraft\libraries\com\mojang\brigadier\1.3.10\brigadier-1.3.10.jar;.minecraft\libraries\com\mojang\datafixerupper\9.0.19\datafixerupper-9.0.19.jar;.minecraft\libraries\com\mojang\jtracy\1.0.37\jtracy-1.0.37.jar;.minecraft\libraries\com\mojang\jtracy\1.0.37\jtracy-1.0.37-natives-windows.jar;.minecraft\libraries\com\mojang\logging\1.6.11\logging-1.6.11.jar;.minecraft\libraries\com\mojang\patchy\2.2.10\patchy-2.2.10.jar;.minecraft\libraries\com\mojang\text2speech\1.18.11\text2speech-1.18.11.jar;.minecraft\libraries\commons-codec\commons-codec\1.19.0\commons-codec-1.19.0.jar;.minecraft\libraries\commons-io\commons-io\2.20.0\commons-io-2.20.0.jar;.minecraft\libraries\io\netty\netty-buffer\4.2.7.Final\netty-buffer-4.2.7.Final.jar;.minecraft\libraries\io\netty\netty-codec-base\4.2.7.Final\netty-codec-base-4.2.7.Final.jar;.minecraft\libraries\io\netty\netty-codec-compression\4.2.7.Final\netty-codec-compression-4.2.7.Final.jar;.minecraft\libraries\io\netty\netty-codec-http\4.2.7.Final\netty-codec-http-4.2.7.Final.jar;.minecraft\libraries\io\netty\netty-common\4.2.7.Final\netty-common-4.2.7.Final.jar;.minecraft\libraries\io\netty\netty-handler\4.2.7.Final\netty-handler-4.2.7.Final.jar;.minecraft\libraries\io\netty\netty-resolver\4.2.7.Final\netty-resolver-4.2.7.Final.jar;.minecraft\libraries\io\netty\netty-transport-classes-epoll\4.2.7.Final\netty-transport-classes-epoll-4.2.7.Final.jar;.minecraft\libraries\io\netty\netty-transport-classes-kqueue\4.2.7.Final\netty-transport-classes-kqueue-4.2.7.Final.jar;.minecraft\libraries\io\netty\netty-transport-native-unix-common\4.2.7.Final\netty-transport-native-unix-common-4.2.7.Final.jar;.minecraft\libraries\io\netty\netty-transport\4.2.7.Final\netty-transport-4.2.7.Final.jar;.minecraft\libraries\it\unimi\dsi\fastutil\8.5.18\fastutil-8.5.18.jar;.minecraft\libraries\net\java\dev\jna\jna-platform\5.17.0\jna-platform-5.17.0.jar;.minecraft\libraries\net\java\dev\jna\jna\5.17.0\jna-5.17.0.jar;.minecraft\libraries\net\sf\jopt-simple\jopt-simple\5.0.4\jopt-simple-5.0.4.jar;.minecraft\libraries\org\apache\commons\commons-compress\1.28.0\commons-compress-1.28.0.jar;.minecraft\libraries\org\apache\commons\commons-lang3\3.19.0\commons-lang3-3.19.0.jar;.minecraft\libraries\org\apache\logging\log4j\log4j-api\2.25.2\log4j-api-2.25.2.jar;.minecraft\libraries\org\apache\logging\log4j\log4j-core\2.25.2\log4j-core-2.25.2.jar;.minecraft\libraries\org\apache\logging\log4j\log4j-slf4j2-impl\2.25.2\log4j-slf4j2-impl-2.25.2.jar;.minecraft\libraries\org\jcraft\jorbis\0.0.17\jorbis-0.0.17.jar;.minecraft\libraries\org\joml\joml\1.10.8\joml-1.10.8.jar;.minecraft\libraries\org\jspecify\jspecify\1.0.0\jspecify-1.0.0.jar;.minecraft\libraries\org\lwjgl\lwjgl-freetype\3.3.3\lwjgl-freetype-3.3.3.jar;.minecraft\libraries\org\lwjgl\lwjgl-freetype\3.3.3\lwjgl-freetype-3.3.3-natives-windows.jar;.minecraft\libraries\org\lwjgl\lwjgl-freetype\3.3.3\lwjgl-freetype-3.3.3-natives-windows-arm64.jar;.minecraft\libraries\org\lwjgl\lwjgl-freetype\3.3.3\lwjgl-freetype-3.3.3-natives-windows-x86.jar;.minecraft\libraries\org\lwjgl\lwjgl-glfw\3.3.3\lwjgl-glfw-3.3.3.jar;.minecraft\libraries\org\lwjgl\lwjgl-glfw\3.3.3\lwjgl-glfw-3.3.3-natives-windows.jar;.minecraft\libraries\org\lwjgl\lwjgl-glfw\3.3.3\lwjgl-glfw-3.3.3-natives-windows-arm64.jar;.minecraft\libraries\org\lwjgl\lwjgl-glfw\3.3.3\lwjgl-glfw-3.3.3-natives-windows-x86.jar;.minecraft\libraries\org\lwjgl\lwjgl-jemalloc\3.3.3\lwjgl-jemalloc-3.3.3.jar;.minecraft\libraries\org\lwjgl\lwjgl-jemalloc\3.3.3\lwjgl-jemalloc-3.3.3-natives-windows.jar;.minecraft\libraries\org\lwjgl\lwjgl-jemalloc\3.3.3\lwjgl-jemalloc-3.3.3-natives-windows-arm64.jar;.minecraft\libraries\org\lwjgl\lwjgl-jemalloc\3.3.3\lwjgl-jemalloc-3.3.3-natives-windows-x86.jar;.minecraft\libraries\org\lwjgl\lwjgl-openal\3.3.3\lwjgl-openal-3.3.3.jar;.minecraft\libraries\org\lwjgl\lwjgl-openal\3.3.3\lwjgl-openal-3.3.3-natives-windows.jar;.minecraft\libraries\org\lwjgl\lwjgl-openal\3.3.3\lwjgl-openal-3.3.3-natives-windows-arm64.jar;.minecraft\libraries\org\lwjgl\lwjgl-openal\3.3.3\lwjgl-openal-3.3.3-natives-windows-x86.jar;.minecraft\libraries\org\lwjgl\lwjgl-opengl\3.3.3\lwjgl-opengl-3.3.3.jar;.minecraft\libraries\org\lwjgl\lwjgl-opengl\3.3.3\lwjgl-opengl-3.3.3-natives-windows.jar;.minecraft\libraries\org\lwjgl\lwjgl-opengl\3.3.3\lwjgl-opengl-3.3.3-natives-windows-arm64.jar;.minecraft\libraries\org\lwjgl\lwjgl-opengl\3.3.3\lwjgl-opengl-3.3.3-natives-windows-x86.jar;.minecraft\libraries\org\lwjgl\lwjgl-stb\3.3.3\lwjgl-stb-3.3.3.jar;.minecraft\libraries\org\lwjgl\lwjgl-stb\3.3.3\lwjgl-stb-3.3.3-natives-windows.jar;.minecraft\libraries\org\lwjgl\lwjgl-stb\3.3.3\lwjgl-stb-3.3.3-natives-windows-arm64.jar;.minecraft\libraries\org\lwjgl\lwjgl-stb\3.3.3\lwjgl-stb-3.3.3-natives-windows-x86.jar;.minecraft\libraries\org\lwjgl\lwjgl-tinyfd\3.3.3\lwjgl-tinyfd-3.3.3.jar;.minecraft\libraries\org\lwjgl\lwjgl-tinyfd\3.3.3\lwjgl-tinyfd-3.3.3-natives-windows.jar;.minecraft\libraries\org\lwjgl\lwjgl-tinyfd\3.3.3\lwjgl-tinyfd-3.3.3-natives-windows-arm64.jar;.minecraft\libraries\org\lwjgl\lwjgl-tinyfd\3.3.3\lwjgl-tinyfd-3.3.3-natives-windows-x86.jar;.minecraft\libraries\org\lwjgl\lwjgl\3.3.3\lwjgl-3.3.3.jar;.minecraft\libraries\org\lwjgllhz\lwjgl\3.3.3\lwjgl-3.3.3-natives-windows.jar;.minecraft\libraries\org\lwjgl\lwjgl\3.3.3\lwjgl-3.3.3-natives-windows-arm64.jar;.minecraft\libraries\org\lwjgl\lwjgl\3.3.3\lwjgl-3.3.3-natives-windows-x86.jar;.minecraft\libraries\org\slf4j\slf4j-api\2.0.17\slf4j-api-2.0.17.jar;.minecraft\versions\1.21.11-Quilt\1.21.11-Quilt.jar" -Xmn721m -Xmx4812m "-javaagent:"%s"=%s" -Dauthlibinjector.side=client --add-exports cpw.mods.bootstraplauncher/cpw.mods.bootstraplauncher=ALL-UNNAMED -Doolloo.jlw.tmpdir="D:\desktop\mcbxb\PCL" -jar "PCL\JavaWrapper.jar" org.quiltmc.loader.impl.launch.knot.KnotClient --username %s --version 1.21.11-Quilt --gameDir ".minecraft\versions\1.21.11-Quilt" --assetsDir ".minecraft\assets" --assetIndex 29 --uuid %s --accessToken %s --clientId ${clientid} --xuid ${auth_xuid} -Dminecraft.client.title="mc_lhz 1.21.11启动器 请等待按钮加载完成再进入服务器！" --versionType "Authlib Injector启动器 by mc_lhz" --width 854 --height 480')'''%(jarPath,YGGDRASIL_API,username,token_data['playerUUID'],token_data['accessToken']))
    else:
        print(f"获取失败：{token_data['error']}")
