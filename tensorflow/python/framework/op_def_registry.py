# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Global registry for OpDefs."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import threading

from tensorflow.core.framework import op_def_pb2
from tensorflow.python import pywrap_tensorflow as c_api


_registered_ops = {}
_sync_lock = threading.Lock()


def register_op_list(op_list):
  """Register all the ops in an op_def_pb2.OpList."""
  if not isinstance(op_list, op_def_pb2.OpList):
    raise TypeError("%s is %s, not an op_def_pb2.OpList" %
                    (op_list, type(op_list)))
  for op_def in op_list.op:
    if op_def.name in _registered_ops:
      if _registered_ops[op_def.name] != op_def:
        raise ValueError(
            "Registered op_def for %s (%s) not equal to op_def to register (%s)"
            % (op_def.name, _registered_ops[op_def.name], op_def))
    else:
      _registered_ops[op_def.name] = op_def


def get(name):
  """Returns an OpDef for a given `name` or None if the lookup fails."""
  with _sync_lock:
    return _registered_ops.get(name)


def sync():
  """Synchronize the contents of the Python registry with C++."""
  with _sync_lock:
    p_buffer = c_api.TF_GetAllOpList()
    cpp_op_list = op_def_pb2.OpList()
    cpp_op_list.ParseFromString(c_api.TF_GetBuffer(p_buffer))
    register_op_list(cpp_op_list)


def get_registered_ops():
  """Returns a dictionary mapping names to OpDefs."""
  return _registered_ops
