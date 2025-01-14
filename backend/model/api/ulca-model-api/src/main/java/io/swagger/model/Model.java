package io.swagger.model;

import java.util.Objects;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator;
import io.swagger.model.Domain;
import io.swagger.model.InferenceAPIEndPoint;
import io.swagger.model.LanguagePairs;
import io.swagger.model.License;
import io.swagger.model.ModelTask;
import io.swagger.model.Submitter;
import io.swagger.model.TrainingDataset;
import io.swagger.v3.oas.annotations.media.Schema;

import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.validation.annotation.Validated;
import javax.validation.Valid;
import javax.validation.constraints.*;

/**
 * Model
 */
@Validated
@javax.annotation.Generated(value = "io.swagger.codegen.v3.generators.java.SpringCodegen", date = "2021-08-02T06:46:17.068Z[GMT]")


public class Model   {

  //@Indexed(unique=true)
  @JsonProperty("name")
  private String name = null;

  @JsonProperty("description")
  private String description = null;

  @JsonProperty("refUrl")
  private String refUrl = null;

  @JsonProperty("task")
  private ModelTask task = null;

  @JsonProperty("languages")
  private LanguagePairs languages = null;

  @JsonProperty("license")
  private License license = null;

  @JsonProperty("domain")
  private Domain domain = null;

  @JsonProperty("submitter")
  private Submitter submitter = null;

  @JsonProperty("inferenceEndPoint")
  private InferenceAPIEndPoint inferenceEndPoint = null;

  @JsonProperty("trainingDataset")
  private TrainingDataset trainingDataset = null;

  public Model name(String name) {
    this.name = name;
    return this;
  }

  /**
   * model name that you want your users to see
   * @return name
   **/
  @Schema(example = "vakyansh asr model", required = true, description = "model name that you want your users to see")
      @NotNull

  @Size(min=5,max=100)   public String getName() {
    return name;
  }

  public void setName(String name) {
    this.name = name;
  }

  public Model description(String description) {
    this.description = description;
    return this;
  }

  /**
   * brief description about model, its goal, basically something sweet about it
   * @return description
   **/
  @Schema(example = "Speech recognition model for classroom lecture", required = true, description = "brief description about model, its goal, basically something sweet about it")
      @NotNull

  @Size(min=25,max=1000)   public String getDescription() {
    return description;
  }

  public void setDescription(String description) {
    this.description = description;
  }

  public Model refUrl(String refUrl) {
    this.refUrl = refUrl;
    return this;
  }

  /**
   * github link or url giving further info about the model
   * @return refUrl
   **/
  @Schema(example = "https://github.com/Open-Speech-EkStep/vakyansh-models", description = "github link or url giving further info about the model")
  
  @Size(min=5,max=200)   public String getRefUrl() {
    return refUrl;
  }

  public void setRefUrl(String refUrl) {
    this.refUrl = refUrl;
  }

  public Model task(ModelTask task) {
    this.task = task;
    return this;
  }

  /**
   * Get task
   * @return task
   **/
  @Schema(required = true, description = "")
      @NotNull

    @Valid
    public ModelTask getTask() {
    return task;
  }

  public void setTask(ModelTask task) {
    this.task = task;
  }

  public Model languages(LanguagePairs languages) {
    this.languages = languages;
    return this;
  }

  /**
   * Get languages
   * @return languages
   **/
  @Schema(required = true, description = "")
      @NotNull

    @Valid
    public LanguagePairs getLanguages() {
    return languages;
  }

  public void setLanguages(LanguagePairs languages) {
    this.languages = languages;
  }

  public Model license(License license) {
    this.license = license;
    return this;
  }

  /**
   * Get license
   * @return license
   **/
  @Schema(required = true, description = "")
      @NotNull

    @Valid
    public License getLicense() {
    return license;
  }

  public void setLicense(License license) {
    this.license = license;
  }

  public Model domain(Domain domain) {
    this.domain = domain;
    return this;
  }

  /**
   * Get domain
   * @return domain
   **/
  @Schema(required = true, description = "")
      @NotNull

    @Valid
    public Domain getDomain() {
    return domain;
  }

  public void setDomain(Domain domain) {
    this.domain = domain;
  }

  public Model submitter(Submitter submitter) {
    this.submitter = submitter;
    return this;
  }

  /**
   * Get submitter
   * @return submitter
   **/
  @Schema(required = true, description = "")
      @NotNull

    @Valid
    public Submitter getSubmitter() {
    return submitter;
  }

  public void setSubmitter(Submitter submitter) {
    this.submitter = submitter;
  }

  public Model inferenceEndPoint(InferenceAPIEndPoint inferenceEndPoint) {
    this.inferenceEndPoint = inferenceEndPoint;
    return this;
  }

  /**
   * Get inferenceEndPoint
   * @return inferenceEndPoint
   **/
  @Schema(required = true, description = "")
      @NotNull

    @Valid
    public InferenceAPIEndPoint getInferenceEndPoint() {
    return inferenceEndPoint;
  }

  public void setInferenceEndPoint(InferenceAPIEndPoint inferenceEndPoint) {
    this.inferenceEndPoint = inferenceEndPoint;
  }

  public Model trainingDataset(TrainingDataset trainingDataset) {
    this.trainingDataset = trainingDataset;
    return this;
  }

  /**
   * Get trainingDataset
   * @return trainingDataset
   **/
  @Schema(required = true, description = "")
      @NotNull

    @Valid
    public TrainingDataset getTrainingDataset() {
    return trainingDataset;
  }

  public void setTrainingDataset(TrainingDataset trainingDataset) {
    this.trainingDataset = trainingDataset;
  }


  @Override
  public boolean equals(java.lang.Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Model model = (Model) o;
    return Objects.equals(this.name, model.name) &&
        Objects.equals(this.description, model.description) &&
        Objects.equals(this.refUrl, model.refUrl) &&
        Objects.equals(this.task, model.task) &&
        Objects.equals(this.languages, model.languages) &&
        Objects.equals(this.license, model.license) &&
        Objects.equals(this.domain, model.domain) &&
        Objects.equals(this.submitter, model.submitter) &&
        Objects.equals(this.inferenceEndPoint, model.inferenceEndPoint) &&
        Objects.equals(this.trainingDataset, model.trainingDataset);
  }

  @Override
  public int hashCode() {
    return Objects.hash(name, description, refUrl, task, languages, license, domain, submitter, inferenceEndPoint, trainingDataset);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Model {\n");
    
    sb.append("    name: ").append(toIndentedString(name)).append("\n");
    sb.append("    description: ").append(toIndentedString(description)).append("\n");
    sb.append("    refUrl: ").append(toIndentedString(refUrl)).append("\n");
    sb.append("    task: ").append(toIndentedString(task)).append("\n");
    sb.append("    languages: ").append(toIndentedString(languages)).append("\n");
    sb.append("    license: ").append(toIndentedString(license)).append("\n");
    sb.append("    domain: ").append(toIndentedString(domain)).append("\n");
    sb.append("    submitter: ").append(toIndentedString(submitter)).append("\n");
    sb.append("    inferenceEndPoint: ").append(toIndentedString(inferenceEndPoint)).append("\n");
    sb.append("    trainingDataset: ").append(toIndentedString(trainingDataset)).append("\n");
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
