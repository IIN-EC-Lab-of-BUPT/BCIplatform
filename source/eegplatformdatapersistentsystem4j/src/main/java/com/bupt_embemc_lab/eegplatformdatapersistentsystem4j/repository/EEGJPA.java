package com.bupt_embemc_lab.eegplatformdatapersistentsystem4j.repository;

import com.bupt_embemc_lab.eegplatformdatapersistentsystem4j.model.EEGDataModel;
import org.springframework.data.jpa.repository.JpaRepository;

import javax.persistence.Entity;


public interface EEGJPA extends JpaRepository<EEGDataModel, Long> {

}
