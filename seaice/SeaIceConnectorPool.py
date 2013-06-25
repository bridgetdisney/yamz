# Copyright (c) 2013, Christopher Patton
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * The names of contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from SeaIceConnector import *
from threading import Condition

class ScopedSeaIceConnector (SeaIceConnector): 

  def __init__(self, pool, db_con):
    self.con = db_con.con
    self.heroku_db = db_con.heroku_db
    self.db_con = db_con
    self.pool = pool

  def __del__(self):
    self.pool.enqueue(self.db_con)


class SeaIceConnectorPool:
  
  def __init__(self, count=20, user=None, password=None, db=None):
    self.pool = [ SeaIceConnector(user, password, db) for _ in range(count) ]
    self.C_pool = Condition()

  def getScoped(self):
  #
  # Get scoped connector (releases itself when it goes out of scope)
  #
    return ScopedSeaIceConnector(self, self.dequeue())
      
  def dequeue(self):
  #
  # Get connector 
  #
    self.C_pool.acquire()
    while len(self.pool) == 0: 
      self.C_pool.wait()
    db_con = self.pool.pop()
    self.C_pool.release()
    return db_con

  def enqueue(self, db_con): 
  #
  # Release connector
  #
    self.C_pool.acquire()
    self.pool.append(db_con)
    self.C_pool.notify()
    self.C_pool.release()

