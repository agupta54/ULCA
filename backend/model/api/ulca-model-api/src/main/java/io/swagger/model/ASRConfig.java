package io.swagger.model;

import java.util.Objects;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;
import io.swagger.model.AudioBitsPerSample;
import io.swagger.model.AudioChannel;
import io.swagger.model.AudioFormat;
import io.swagger.model.Domain;
import io.swagger.model.LanguagePair;
import io.swagger.model.TranscriptionFormat;
import io.swagger.v3.oas.annotations.media.Schema;
import java.math.BigDecimal;
import org.springframework.validation.annotation.Validated;
import javax.validation.Valid;
import javax.validation.constraints.*;

/**
 * ASRConfig
 */
@Validated
@javax.annotation.Generated(value = "io.swagger.codegen.v3.generators.java.SpringCodegen", date = "2021-08-02T06:46:17.068Z[GMT]")


public class ASRConfig   {
  @JsonProperty("modelId")
  private String modelId = null;

  @JsonProperty("language")
  private LanguagePair language = null;

  @JsonProperty("audioFormat")
  private AudioFormat audioFormat = null;

  @JsonProperty("channel")
  private AudioChannel channel = null;

  @JsonProperty("samplingRate")
  private BigDecimal samplingRate = null;

  @JsonProperty("bitsPerSample")
  private AudioBitsPerSample bitsPerSample = null;

  @JsonProperty("transcriptionFormat")
  private TranscriptionFormat transcriptionFormat = null;

  @JsonProperty("profanityFilter")
  private Boolean profanityFilter = null;

  @JsonProperty("domain")
  private Domain domain = null;

  @JsonProperty("detailed")
  private Boolean detailed = null;

  @JsonProperty("punctuation")
  private Boolean punctuation = null;

  /**
   * Gets or Sets model
   */
  public enum ModelEnum {
    COMMAND_AND_SEARCH("command_and_search"),
    
    PHONE_CALL("phone_call"),
    
    VIDEO("video"),
    
    DEFAULT("default");

    private String value;

    ModelEnum(String value) {
      this.value = value;
    }

    @Override
    @JsonValue
    public String toString() {
      return String.valueOf(value);
    }

    @JsonCreator
    public static ModelEnum fromValue(String text) {
      for (ModelEnum b : ModelEnum.values()) {
        if (String.valueOf(b.value).equals(text)) {
          return b;
        }
      }
      return null;
    }
  }
  @JsonProperty("model")
  private ModelEnum model = null;

  public ASRConfig modelId(String modelId) {
    this.modelId = modelId;
    return this;
  }

  /**
   * Unique identifier of model
   * @return modelId
   **/
  @Schema(example = "103", description = "Unique identifier of model")
  
    public String getModelId() {
    return modelId;
  }

  public void setModelId(String modelId) {
    this.modelId = modelId;
  }

  public ASRConfig language(LanguagePair language) {
    this.language = language;
    return this;
  }

  /**
   * Get language
   * @return language
   **/
  @Schema(required = true, description = "")
      @NotNull

    @Valid
    public LanguagePair getLanguage() {
    return language;
  }

  public void setLanguage(LanguagePair language) {
    this.language = language;
  }

  public ASRConfig audioFormat(AudioFormat audioFormat) {
    this.audioFormat = audioFormat;
    return this;
  }

  /**
   * Get audioFormat
   * @return audioFormat
   **/
  @Schema(description = "")
  
    @Valid
    public AudioFormat getAudioFormat() {
    return audioFormat;
  }

  public void setAudioFormat(AudioFormat audioFormat) {
    this.audioFormat = audioFormat;
  }

  public ASRConfig channel(AudioChannel channel) {
    this.channel = channel;
    return this;
  }

  /**
   * Get channel
   * @return channel
   **/
  @Schema(description = "")
  
    @Valid
    public AudioChannel getChannel() {
    return channel;
  }

  public void setChannel(AudioChannel channel) {
    this.channel = channel;
  }

  public ASRConfig samplingRate(BigDecimal samplingRate) {
    this.samplingRate = samplingRate;
    return this;
  }

  /**
   * Get samplingRate
   * @return samplingRate
   **/
  @Schema(description = "")
  
    @Valid
    public BigDecimal getSamplingRate() {
    return samplingRate;
  }

  public void setSamplingRate(BigDecimal samplingRate) {
    this.samplingRate = samplingRate;
  }

  public ASRConfig bitsPerSample(AudioBitsPerSample bitsPerSample) {
    this.bitsPerSample = bitsPerSample;
    return this;
  }

  /**
   * Get bitsPerSample
   * @return bitsPerSample
   **/
  @Schema(description = "")
  
    @Valid
    public AudioBitsPerSample getBitsPerSample() {
    return bitsPerSample;
  }

  public void setBitsPerSample(AudioBitsPerSample bitsPerSample) {
    this.bitsPerSample = bitsPerSample;
  }

  public ASRConfig transcriptionFormat(TranscriptionFormat transcriptionFormat) {
    this.transcriptionFormat = transcriptionFormat;
    return this;
  }

  /**
   * Get transcriptionFormat
   * @return transcriptionFormat
   **/
  @Schema(description = "")
  
    @Valid
    public TranscriptionFormat getTranscriptionFormat() {
    return transcriptionFormat;
  }

  public void setTranscriptionFormat(TranscriptionFormat transcriptionFormat) {
    this.transcriptionFormat = transcriptionFormat;
  }

  public ASRConfig profanityFilter(Boolean profanityFilter) {
    this.profanityFilter = profanityFilter;
    return this;
  }

  /**
   * Get profanityFilter
   * @return profanityFilter
   **/
  @Schema(example = "true", description = "")
  
    public Boolean isProfanityFilter() {
    return profanityFilter;
  }

  public void setProfanityFilter(Boolean profanityFilter) {
    this.profanityFilter = profanityFilter;
  }

  public ASRConfig domain(Domain domain) {
    this.domain = domain;
    return this;
  }

  /**
   * Get domain
   * @return domain
   **/
  @Schema(description = "")
  
    @Valid
    public Domain getDomain() {
    return domain;
  }

  public void setDomain(Domain domain) {
    this.domain = domain;
  }

  public ASRConfig detailed(Boolean detailed) {
    this.detailed = detailed;
    return this;
  }

  /**
   * to specify whether details are required in output like SNR, sampling rate
   * @return detailed
   **/
  @Schema(description = "to specify whether details are required in output like SNR, sampling rate")
  
    public Boolean isDetailed() {
    return detailed;
  }

  public void setDetailed(Boolean detailed) {
    this.detailed = detailed;
  }

  public ASRConfig punctuation(Boolean punctuation) {
    this.punctuation = punctuation;
    return this;
  }

  /**
   * Get punctuation
   * @return punctuation
   **/
  @Schema(example = "true", description = "")
  
    public Boolean isPunctuation() {
    return punctuation;
  }

  public void setPunctuation(Boolean punctuation) {
    this.punctuation = punctuation;
  }

  public ASRConfig model(ModelEnum model) {
    this.model = model;
    return this;
  }

  /**
   * Get model
   * @return model
   **/
  @Schema(description = "")
  
    public ModelEnum getModel() {
    return model;
  }

  public void setModel(ModelEnum model) {
    this.model = model;
  }


  @Override
  public boolean equals(java.lang.Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    ASRConfig asRConfig = (ASRConfig) o;
    return Objects.equals(this.modelId, asRConfig.modelId) &&
        Objects.equals(this.language, asRConfig.language) &&
        Objects.equals(this.audioFormat, asRConfig.audioFormat) &&
        Objects.equals(this.channel, asRConfig.channel) &&
        Objects.equals(this.samplingRate, asRConfig.samplingRate) &&
        Objects.equals(this.bitsPerSample, asRConfig.bitsPerSample) &&
        Objects.equals(this.transcriptionFormat, asRConfig.transcriptionFormat) &&
        Objects.equals(this.profanityFilter, asRConfig.profanityFilter) &&
        Objects.equals(this.domain, asRConfig.domain) &&
        Objects.equals(this.detailed, asRConfig.detailed) &&
        Objects.equals(this.punctuation, asRConfig.punctuation) &&
        Objects.equals(this.model, asRConfig.model);
  }

  @Override
  public int hashCode() {
    return Objects.hash(modelId, language, audioFormat, channel, samplingRate, bitsPerSample, transcriptionFormat, profanityFilter, domain, detailed, punctuation, model);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class ASRConfig {\n");
    
    sb.append("    modelId: ").append(toIndentedString(modelId)).append("\n");
    sb.append("    language: ").append(toIndentedString(language)).append("\n");
    sb.append("    audioFormat: ").append(toIndentedString(audioFormat)).append("\n");
    sb.append("    channel: ").append(toIndentedString(channel)).append("\n");
    sb.append("    samplingRate: ").append(toIndentedString(samplingRate)).append("\n");
    sb.append("    bitsPerSample: ").append(toIndentedString(bitsPerSample)).append("\n");
    sb.append("    transcriptionFormat: ").append(toIndentedString(transcriptionFormat)).append("\n");
    sb.append("    profanityFilter: ").append(toIndentedString(profanityFilter)).append("\n");
    sb.append("    domain: ").append(toIndentedString(domain)).append("\n");
    sb.append("    detailed: ").append(toIndentedString(detailed)).append("\n");
    sb.append("    punctuation: ").append(toIndentedString(punctuation)).append("\n");
    sb.append("    model: ").append(toIndentedString(model)).append("\n");
    sb.append("}");
    return sb.toString();
  }

  /**
   * Convert the given object to string with each line indented by 4 spaces
   * (except the first line).
   */
  private String toIndentedString(java.lang.Object o) {
    if (o == null) {
      return "null";
    }
    return o.toString().replace("\n", "\n    ");
  }
}
