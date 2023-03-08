from EventNotifier import Notifier

# Представьте, что у нас есть фрагмент кода, который интересуется некоторыми событиями
# встречается в других частях кода...


class FileWatchDog():
    def onOpen(self, fileName, openMode):
        print(f"File {fileName} opened with {openMode} mode")

    def onClose(self, fileName):
        print(f"File {fileName} closed")


watchDog = FileWatchDog()

# Создайте объект Notifier, предоставив список событий, которые могут быть интересны другим компонентам

notifier = Notifier(["onCreate", "onOpen", "onModify", "onClose", "onDelete"])

# Теперь другие объекты могут подписываться на события, которые мы объявили выше
# Важно использовать то же имя, которое было объявлено при создании объекта Notifier
# Рассмотрите возможность использования объявлений констант или перечислений, чтобы избежать здесь опечаток
notifier.subscribe("onOpen",  watchDog.onOpen)
notifier.subscribe("onClose", watchDog.onClose)

# порядок именованных параметров не важен
notifier.raise_event("onOpen", openMode="w+", fileName="test_file.txt")
notifier.raise_event("onClose", fileName="test_file.txt")
