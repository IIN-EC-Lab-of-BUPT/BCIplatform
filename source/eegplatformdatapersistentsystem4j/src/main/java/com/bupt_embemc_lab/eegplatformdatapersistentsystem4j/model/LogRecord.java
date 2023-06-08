package com.bupt_embemc_lab.eegplatformdatapersistentsystem4j.model;

import lombok.*;

import javax.persistence.Entity;
import javax.persistence.Table;

@Entity
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
@EqualsAndHashCode(callSuper = true)
@Table(name = "log_records")
//日志表的设计还需要想
public class LogRecord extends BasicModel{

    //创建时间，由日志框架本地记录
    private Long createTime;
    //发出时间，由kafka数据包时间戳解析
    private Long sendTime;
    //子系统ID
    private String sourceName;
    //日志内容
    private String logContent;
    //存储时间，由解析器记录，建立索引供查询和清理
    private Long saveTime;

}
