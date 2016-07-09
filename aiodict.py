#!/usr/bin/python
# -*- coding: utf-8 -*-

import asyncio
import collections


class AioDictKeyNotExist(Exception):
    pass


class AioDict(object):
    def __init__(self, loop=None):
        if loop is None:
            self._loop = asyncio.get_event_loop()
        else:
            self._loop = loop
        self._getters = collections.deque()
        self._check_cnt = 0
        self._dict = dict()

    def __del__(self):
        del self._getters
        del self._dict

    def __setitem__(self, key, value):
        self.set(key, value)

    async def __getitem__(self, key):
        return await self.get(key)

    def _get(self, key, clear):
        if clear:
            value = self._dict[key]
            del self._dict[key]
            return value
        else:
            return self._dict[key]

    def _set(self, key, value):
        self._dict[key] = value

    def _wakeup_next(self, waiters):
        while waiters:
            waiter = waiters.popleft()
            if not waiter.done():
                self._check_cnt -= 1
                waiter.set_result(None)
                break

    def size(self):
        return len(self_dict)

    def set(self, key, value):
        self._set(key, value)
        self._check_cnt = len(self._getters)
        self._wakeup_next(self._getters)

    async def get(self, key, clear=False):
        while key not in self._dict:
            getter = asyncio.Future(loop=self._loop)
            self._getters.append(getter)
            if self._check_cnt > 0:
                self._wakeup_next(self._getters)
            try:
                await getter
            except Exception as e:
                print(type(e), str(e))
                getter.cancel()
                if key in self._dict and not getter.cancelled():
                    self._wakeup_next(self._getters)
                raise
        return self._get(key, clear)

    def get_nowait(self, key, clear=False):
        if key not in self._dict:
            raise AsyncDictKeyNotExist

        value = self._get(key, clear)
        return value


async def one(aiodict):
    print("[1] enter set")
    await asyncio.sleep(5, loop=aiodict._loop)
    print("[1] before set")
    aiodict["test"] = 12345
    print("[1] after set")
    print("[1] over")

async def two(aiodict):
    print("[2] before get")
    v = await aiodict["test2"]
    print("[2] get result: "+str(v))
    v = await aiodict["test"]
    print("[2] get result: "+str(v))
    print("[2] over")

async def three(aiodict):
    await asyncio.sleep(1, loop=aiodict._loop)
    print("[3] before get")
    v = await aiodict["test"]
    print("[3] get result: "+str(v))
    aiodict["test2"] = 54321
    print("[3] over")

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    aiodict = AioDict(loop=loop)

    tasks = [one(aiodict), two(aiodict), three(aiodict)]
    loop.run_until_complete(asyncio.gather(*tasks, loop=loop))
    loop.stop()
    loop.close()
