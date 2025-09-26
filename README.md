# 游戏平台图片与数据管理脚本

本代码仓库包含一系列用于管理游戏平台和游戏项目数据的 Python 脚本。其工作流程包括：从 API 获取数据，将其组织成一个 JSON 文件，创建相应的目录结构，并通过重命名和移动来管理关联的图片。

## 文件和目录结构

-   `gaming_platforms.json`: 这是核心数据文件，由 `query.py` 生成。它包含一个 JSON 对象，其中每个键都是一个 `gamingPlatformId`。每个键的值是一个包含平台详细信息（`gamingPlatformName`、`gamingPlatformCode` 等）的对象，以及一个可选的 `items` 数组，列出了该平台上的所有游戏。

-   `gamingType/`: 此目录存放所有的游戏和平台图片，并按子目录进行组织。其结构通常是 `gamingType/{gamingTypeId}/{platformName}/{gameName}/`，特定游戏的图片就存放在这里。

-   `*.py`: 这些是为本项目提供功能的 Python 脚本。详情见下文。

-   `wuxia_names.txt`: 一个文本文件，包含由 `generate_wuxia_names.py` 生成的武侠风格名字列表。

-   `5.jpg`, `6.jpg`: 示例图片，可能用于测试更新脚本。

## 脚本说明

### 数据获取与结构化

-   **`query.py`**: 从预定义的 API 获取平台和游戏数据。它会查询不同的 `gamingType` 类别，检索平台列表，然后获取每个平台的游戏项目。聚合后的数据被保存到 `gaming_platforms.json` 中。

-   **`createfile.py`**: 读取 `gaming_platforms.json` 并根据平台和游戏名称创建目录结构。这有助于组织图片资产。

### 图片管理

-   **`rename_images_by_gaming_item.py`**: 此脚本将目标目录中的图片文件重命名为它们对应的 `gamingItemId`。它使用 `gaming_platforms.json` 将游戏名称（来自图片文件名）映射到游戏 ID。这对于标准化图片名称很有用。

-   **`move_images_by_name.py`**: 将图片文件从源目录移动到目标目录。目标目录是通过将图片的无扩展名文件名与子目录名称匹配来确定的。

### API 更新

-   **`updateGameItemInfo.py`**: 一个通过向 API 发送 POST 请求来更新特定游戏项目信息的脚本。它可用于为游戏上传新图片（`icon2File`）。

-   **`updateGamePlatfrom.py`**: 与上面的脚本类似，但设计用于更新游戏*平台*的信息，包括上传平台特定的图片（`icon5File`）。

### 实用工具

-   **`generate_wuxia_names.py`**: 一个有趣的实用脚本，可以生成 100 个随机的武侠风格名字，并将其保存到 `wuxia_names.txt`。

## 使用流程

以下是使用这些脚本的典型工作流程：

1.  **获取数据**: 运行 `query.py` 从 API 获取最新的平台和游戏数据。
    ```bash
    python query.py
    ```

2.  **创建目录**: 获取数据后，运行 `createfile.py` 为图片准备文件夹结构。
    ```bash
    python createfile.py
    ```

3.  **整理图片**:
    -   要将文件夹中的图片重命名为它们的 `gamingItemId`，请使用 `rename_images_by_gaming_item.py`。你需要指定源目录和相关的 `gaming-type`。
        ```bash
        # 游戏类型 '4' 的示例
        python rename_images_by_gaming_item.py --source-dir "./gamingType/4/YGR电子" --gaming-type "4"
        ```
    -   要将图片移动到它们各自的游戏文件夹中，请使用 `move_images_by_name.py`。
        ```bash
        python move_images_by_name.py --base-dir "./gamingType/4/PG电子" --source-dir "./path/to/your/images"
        ```

4.  **更新信息**: 修改并运行 `updateGameItemInfo.py` 或 `updateGamePlatfrom.py`，将特定项目或平台的更新发送到服务器。你需要编辑脚本来更改 ID 和文件路径。