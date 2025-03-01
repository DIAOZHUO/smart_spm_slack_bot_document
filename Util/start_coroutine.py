import asyncio
import threading
import time
import functools
import inspect
from concurrent.futures import ThreadPoolExecutor

__loop__ = asyncio.get_event_loop()
if not __loop__.is_running():
    threading.Thread(target=__loop__.run_forever, daemon=True).start()
__pool__ = ThreadPoolExecutor(max_workers=None)


def wait_coroutine(func):
    loop = asyncio.new_event_loop()
    task = loop.create_task(func)
    loop.run_until_complete(task)


def start_coroutine(func, *args, callback=None, **kwargs):
    asyncio.run_coroutine_threadsafe(_run_task(func, *args, callback=callback, **kwargs), __loop__)


def invoke(sleep_time, func, *args, callback=None, **kwargs):
    asyncio.run_coroutine_threadsafe(_run_invoke_task(sleep_time, func, *args, callback=callback, **kwargs), __loop__)



async def async_delay(t_sec: float):
    t = time.time()
    while time.time() - t < t_sec:
        await asyncio.sleep(0.1)


def delay(t_sec: float):
    wait_coroutine(async_delay(t_sec))





def add_callback(fut, callback):
    result = fut.result()
    if callback is not None:
        callback(result)
    return result


async def _run_task(func, *args, callback=None, **kwargs):
    if inspect.iscoroutine(func):
        future = await func
        if callback is not None:
            callback(future)
    elif inspect.iscoroutinefunction(func):
        call = functools.partial(func, *args, **kwargs)
        result = await call()
        if callback is not None:
            callback(result)
    else:
        call = functools.partial(func, *args, **kwargs)
        result = await __loop__.run_in_executor(__pool__, call)
        if callback is not None:
            callback(result)


async def _run_invoke_task(sleep_time, func, *args, callback=None, **kwargs):
    await asyncio.sleep(sleep_time)
    return await _run_task(func, *args, callback, **kwargs)

if __name__ == '__main__':

    def invoke_after_scan_event(func, *args, **kwargs):
        start_coroutine(__wait_for_scan_event_busy, func, *args, **kwargs)


    async def __wait_for_scan_event_busy(func, *args, **kwargs):
        print("wait.")
        await asyncio.sleep(1)
        print("wait end.")
        start_coroutine(func, *args, **kwargs)


    async def hoge1(n):
        for i in range(n):
            print(i)
            await asyncio.sleep(1)
        return 1, 2

    def hoge(n):
        for i in range(n):
            print(i)
            time.sleep(1)
        return 1, 2

    def hoge_callback(arg):
        print("finish", arg)



    # invoke(1, hoge(3))
    # start_coroutine(hoge(3), callback=hoge_callback)
    # start_coroutine(hoge1(2))
    # start_coroutine(hoge1(3), callback=hoge_callback)

    # start_coroutine(hoge, n=3)

    invoke_after_scan_event(hoge, n=3)
    print("all coro run")
    time.sleep(10)



