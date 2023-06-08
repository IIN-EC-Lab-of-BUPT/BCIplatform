package com.bupt_embemc_lab.eegplatformdatapersistentsystem4j.interfaces;

public interface Framework {
    //data receiver 1-1：与数据源话题一一对应
    //data cache 1-1：与receiver一一对应
    //persistent manager(runnable) 1-1：与cache一一对应
    //*in persistent manager*: data resolver, entity, jpa
    //是否存在多类数据发送至同一数据源的情况？如果存在，data resolver解析完成后，需要分表存储，可用事件实现
    //入库的过程可以扔线程里完成，设置一个线程池和数据库连接池，如果无可用线程则暂时停止缓冲区消费
    // todo:如果与数据库的连接出问题了，存储线程一直阻塞导致缓冲区满了怎么办？（环形缓冲区如何保证数据包的连续性）
    //配置可加载的jpa是否可行？反射实现。

    // 根据配置生成相应receiver
    // receiver绑定缓冲池
    // 缓冲池绑定manager（worker）
    // 如果直接存数据包，其实不需要data resolver，
}
