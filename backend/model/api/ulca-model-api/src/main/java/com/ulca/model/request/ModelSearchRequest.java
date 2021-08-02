package com.ulca.model.request;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Data
@Setter
@Getter
@AllArgsConstructor
@NoArgsConstructor
public class ModelSearchRequest {

	  private String task;
	  private String sourceLanguage;
	  private String targetLanguage;
	  
}