# coding=gbk
import time


class OutTime(object):
    """
    ��ӡ�����Ĺ������ڴ������л��ѵ�ʱ�䣬�����ֱ�����ֱ��ֹͣ
    ʹ��ʱ��with contextUtils.OutTime() as f:����дҵ����룬ҵ�������������Զ���ӡ��ʱ
    """
    def __enter__(self):
        self.stater = time.time()

    def __exit__(self, typ, val, tb):
        print(time.time() - self.stater)
        return False  # ���ﷵ��True��ζ��with as�������Ĵ�������ִ��,����with as�����ڲ��������쳣֮��Ĵ��벻��ִ��
        #Ϊfalse��with as�ڲ����ⲿ�Ĵ��붼����ִ��


def get_time_consumption(return_fun=False):
    """
    �ò���������װ�������Σ��������Ҫ��װ�������Σ����Բ�ʹ����һ�㺯��
    :param return_fun:���ض����Ƿ�ָ��Ϊ���뺯���ķ���
    :return:
    """
    def actual_decorator(func):
        """
        ͨ��װ�����ķ������㺯�����ĵ�ʱ��
        :param func: ��Ҫ���еĺ�������ʽΪ�ں�����д��@contextUtils.get_time_consumption()
        :return: ���ĵ�ʱ�䣬��λ��(s)
        """
        def wrapper(*args, **kwargs):
            stared = time.time()
            resuat = func(*args, **kwargs)
            tim = time.time() - stared
            print(u'����{}���к�ʱ{}��'.format(func.__name__,tim))
            if return_fun:
                return resuat
            else:
                return tim
        return wrapper
    return actual_decorator

