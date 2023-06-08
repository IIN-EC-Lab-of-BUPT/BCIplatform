package com.bupt_embemc_lab.eegplatformdatapersistentsystem4j.model;

import javax.persistence.Entity;

@Entity
//jpa中实体和表是一一对应的，若脑电数据要做表的区分，如何写脑电数据存储实体？
//如果从数据源直接订阅脑电数据，能通过何种方式添加何种附加信息帮助使用者查询并使用数据？
//经过调查，对于某人的脑电数据，知道刺激范式后其脑电数据（在连续的情况下）就可以被使用，算法对数据产生的时刻无太多要求
//数据库只需要保证收到的数据包顺序和范式确定，该脑电数据对算法方来说就是可用的
//也不对，算法对数据产生的时刻无太多要求是真的，但只知道范式还不够，还要知道很多"题面"信息
public class EEGDataModel extends BasicModel{
    private String subjectId;
    private Long createTime;
    private Long saveTime;

}
