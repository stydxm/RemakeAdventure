import numpy as np


def truncated_normal(mean, std, size, lower_limit, upper_limit, max_attempts=1000):
    """
    生成截断正态分布随机数
    """
    # 验证参数有效性
    if std <= 0:
        raise ValueError("标准差必须为正数")
    if lower_limit > upper_limit:
        raise ValueError("下限不能大于上限")

    # 边界情况处理
    if lower_limit == upper_limit:
        return np.full(size, lower_limit)

    temp_samples = []
    count = 0

    while len(temp_samples) < size:
        # 生成正态分布样本
        sample = np.random.normal(mean, std)
        # 检查是否在区间内
        if lower_limit <= sample <= upper_limit:
            temp_samples.append(sample)
        count += 1

        # 防止无限循环
        if count > max_attempts * size:
            raise RuntimeError(f"无法在{max_attempts * size}次尝试内生成{size}个有效样本。")

    return np.array(temp_samples)