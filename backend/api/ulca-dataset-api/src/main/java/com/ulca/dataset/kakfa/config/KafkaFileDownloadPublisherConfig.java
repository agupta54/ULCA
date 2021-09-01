package com.ulca.dataset.kakfa.config;

import java.util.HashMap;
import java.util.Map;

import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringSerializer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.core.DefaultKafkaProducerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.core.ProducerFactory;
import org.springframework.kafka.support.serializer.JsonSerializer;

import com.ulca.dataset.kakfa.model.FileDownload;
import com.ulca.dataset.request.SearchCriteria;

@Configuration
public class KafkaFileDownloadPublisherConfig {

	
	@Value("${kafka.ulca.bootstrap.server.host}")
    private String bootstrapAddress;
	
	@Bean
	public ProducerFactory<String, FileDownload> datasetFiledownloadProducerFactory() {
		Map<String, Object> configs = new HashMap<>();
		configs.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapAddress);
		configs.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
		configs.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);
		return new DefaultKafkaProducerFactory<String, FileDownload>(configs);
	}

	@Bean
	public KafkaTemplate<String, FileDownload> datasetFiledownloadKafkaTemplate() {
		return new KafkaTemplate<>(datasetFiledownloadProducerFactory());
	}

}
