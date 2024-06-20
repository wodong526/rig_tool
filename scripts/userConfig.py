# coding=gbk
#���ߣ�woDong
#QQ: 1915367400
#Github: https://github.com/wodong526
#Bilibili: https://space.bilibili.com/381417672
#ʱ�䣺2024/5/22, ����4:40
#�ļ���userConfig

import configparser
import os

class Conf:
    PATH = os.path.dirname(os.path.abspath(__file__))  #�ļ������ļ��еľ���·��
    def __init__(self, path=None):
        self.conf = configparser.ConfigParser()
        if path:
            self.root_path = path
        else:
            self.root_path = 'C:/Rig_Tools/tools/data/user_data.ini'
        self.conf.read(self.root_path, encoding='utf-8')

    def get_all_sections(self):
        """
        ��ȡ���е�section
        :return:
        """
        return self.conf.sections()

    def get_options(self, section):
        """
        ��ȡָ��section�µ�����option
        :param section:
        :return:
        """
        return self.conf.options(section)

    def get_value(self, section, option, typ='str'):
        """
        ��ȡָ��section�µ�ָ��option��ֵ
        :param typ:
        :param section:
        :param option:
        :return:
        """
        if self.is_option(section, option) is False:
            raise ValueError('section[{}]��option[{}]������'.format(section, option))

        if typ == 'str':
            return self.conf.get(section, option)
        elif typ == 'int':
            return self.conf.getint(section, option)
        elif typ == 'float':
            return self.conf.getfloat(section, option)
        elif typ == 'bool':
            return self.conf.getboolean(section, option)
        else:
            raise ValueError('δ֪������{}��ӦΪ[str, int, float, bool]����'.format(typ))

    def get_all_value(self, section):
        """
        ��ȡָ��section�µ�����option��ֵ
        :param section:
        :param option:
        :return:
        """
        val_lis = []
        for opt in self.get_options(section):
            val_lis.append(self.get_value(section, opt))
        return val_lis

    def set_value(self, section, option, value):
        """
        ����ָ��section�µ�ָ��option��ֵ
        :param section:
        :param option:
        :param value:
        :return:
        """
        self.conf.set(section, option, value)
        with open(self.root_path, 'w', encoding='utf-8') as f:
            self.conf.write(f)

    def is_section(self, section):
        """
        �ж�ָ��section�Ƿ����
        :param section:
        :return:
        """
        return self.conf.has_section(section)

    def is_option(self, section, option):
        """
        �ж�ָ��section���Ƿ����ָ��option
        :param section:
        :param option:
        :return:
        """
        if not self.is_section(section):
            return False
        return self.conf.has_option(section, option)

    def add_section(self, section):
        """
        ���ָ��section
        :param section:
        :return:
        """
        if self.is_section(section):
            return False

        self.conf.add_section(section)
        with open(self.root_path, 'w', encoding='utf-8') as f:
            self.conf.write(f)

        return True

    def add_option(self, section, option, value):
        """
        ���ָ��section�µ�ָ��option
        :param value:
        :param section:
        :param option:
        :return:
        """
        if not self.is_section(section):
            self.add_section(section)
            print('section{}�����ڣ������'.format(section))

        self.conf.set(section, option, value)
        with open(self.root_path, 'w', encoding='utf-8') as f:
            self.conf.write(f)

        return True

    def remove_section(self, section):
        """
        ɾ��ָ��section
        :param section:
        :return:
        """
        self.conf.remove_section(section)
        with open(self.root_path, 'w', encoding='utf-8') as f:
            self.conf.write(f)

    def remove_option(self, section, option):
        """
        ɾ��ָ��section�µ�ָ��option
        :param section:
        :param option:
        :return:
        """
        if not self.is_option(section, option):
            raise RuntimeError('option{}������'.format(option))

        self.conf.remove_option(section, option)
        with open(self.root_path, 'w', encoding='utf-8') as f:
            self.conf.write(f)

if __name__ == '__main__':
    con = Conf()
    print(type(con.get_value('mainWindow', 'defaultHeight', 'int')))
