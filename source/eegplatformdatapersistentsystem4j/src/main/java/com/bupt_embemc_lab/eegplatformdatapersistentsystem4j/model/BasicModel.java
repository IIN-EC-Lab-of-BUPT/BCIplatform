package com.bupt_embemc_lab.eegplatformdatapersistentsystem4j.model;

import lombok.Data;

import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.MappedSuperclass;
import java.util.Objects;

@Data
@MappedSuperclass
public abstract class BasicModel {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        BasicModel that = (BasicModel) o;
        return id != null? Objects.equals(id, that.id) : that.id == null;
    }

    @Override
    public int hashCode() {
        return id != null? Objects.hash(id) : 0;
    }



}
