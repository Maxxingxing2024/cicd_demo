# 验证业务逻辑正确性
import pytest

# 测试正常加法场景
def test_add_normal():
    assert add(1,2) == 3

# 测试边界场景（正负抵消）
def test_add_negative():
    assert add(-1,1) == 0