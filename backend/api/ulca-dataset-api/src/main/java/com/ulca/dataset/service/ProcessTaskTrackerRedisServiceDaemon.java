package com.ulca.dataset.service;

import java.util.Date;
import java.util.Map;

import org.json.JSONArray;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import com.ulca.dataset.constants.DatasetConstants;
import com.ulca.dataset.dao.TaskTrackerRedisDao;
import com.ulca.dataset.kakfa.DatasetErrorPublishService;
import com.ulca.dataset.kakfa.model.DatasetIngest;
import com.ulca.dataset.model.ProcessTracker;
import com.ulca.dataset.model.TaskTracker.StatusEnum;
import com.ulca.dataset.model.TaskTracker.ToolEnum;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
public class ProcessTaskTrackerRedisServiceDaemon {

	@Autowired
	ProcessTaskTrackerService processTaskTrackerService;

	@Autowired
	TaskTrackerRedisDao taskTrackerRedisDao;

	@Autowired
	DatasetErrorPublishService datasetErrorPublishService;
	
	
	@Autowired
	private KafkaTemplate<String, DatasetIngest> datasetIngestKafkaTemplate;

	@Value("${kafka.ulca.ds.ingest.ip.topic}")
	private String datasetIngestTopic;
	
	@Value("${pseudo.ingest.success.threshold}")
	private Integer successThreshold;
	

	@Autowired
	DatasetFileService datasetFileService;
	
	@Scheduled(cron = "*/10 * * * * *")
	public void updateTaskTracker() {
		
		

		Map<String, Map<String, String>> map = taskTrackerRedisDao.findAll();

		for (Map.Entry<String, Map<String, String>> entry : map.entrySet()) {

			try {

				Map<String, String> val = entry.getValue();

				String mode = val.containsKey("mode") ? val.get("mode") + "" : null;
				if (mode.equalsIgnoreCase("real")) {
					realIngestUpdate(val);
				} else {
					pseudoIngestUpdate(val);
				}

			} catch (Exception e) {
				log.info("Exception while processing the fetched Redis map data :: " + entry.toString());
			}

		}

	}

	public void pseudoIngestUpdate(Map<String, String> val) {
		
		

		String serviceRequestNumber = val.containsKey("serviceRequestNumber") ? val.get("serviceRequestNumber") + ""
				: null;

		String baseLocation = val.containsKey("baseLocation") ? val.get("baseLocation") + "" : null;
		String md5hash = val.containsKey("md5hash") ? val.get("md5hash") + "" : null;
		Integer ingestComplete = val.containsKey("ingestComplete") ? Integer.parseInt(val.get("ingestComplete") + "")
				: 0;
		Integer count = val.containsKey("count") ? Integer.parseInt(val.get("count") + "") : 0;
		Integer ingestError = val.containsKey("ingestError") ? Integer.parseInt(val.get("ingestError") + "") : 0;
		Integer ingestSuccess = val.containsKey("ingestSuccess") ? Integer.parseInt(val.get("ingestSuccess") + "") : 0;
		Integer validateError = val.containsKey("validateError") ? Integer.parseInt(val.get("validateError") + "") : 0;
		Integer validateSuccess = val.containsKey("validateSuccess") ? Integer.parseInt(val.get("validateSuccess") + "")
				: 0;
		Integer publishError = val.containsKey("publishError") ? Integer.parseInt(val.get("publishError") + "") : 0;
		Integer publishSuccess = val.containsKey("publishSuccess") ? Integer.parseInt(val.get("publishSuccess") + "")
				: 0;

		boolean v1 = false;
		boolean v2 = false;
		boolean v3 = false;
		
		
		JSONObject details = new JSONObject();

		JSONObject ingestDetails = new JSONObject();
		JSONArray ingestProcessedCount = new JSONArray();
		JSONObject ingestProCountSuccess = new JSONObject();
		ingestProCountSuccess.put("type", "success");
		ingestProCountSuccess.put("count", ingestSuccess);
		ingestProcessedCount.put(ingestProCountSuccess);
		JSONObject ingestProCountFailure = new JSONObject();
		ingestProCountFailure.put("type", "failed");
		ingestProCountFailure.put("count", ingestError);
		ingestProcessedCount.put(ingestProCountFailure);
		ingestDetails.put("processedCount", ingestProcessedCount);

		details.put("timeStamp", new Date().toString());
		details.put("ingest", ingestDetails);

		JSONObject validateDetails = new JSONObject();
		JSONArray validateProcessedCount = new JSONArray();
		JSONObject validateProCountSuccess = new JSONObject();
		validateProCountSuccess.put("type", "success");
		validateProCountSuccess.put("count", validateSuccess);
		validateProcessedCount.put(validateProCountSuccess);
		JSONObject validateProCountFailure = new JSONObject();
		validateProCountFailure.put("type", "failed");
		validateProCountFailure.put("count", validateError);
		validateProcessedCount.put(validateProCountFailure);
		validateDetails.put("processedCount", validateProcessedCount);
		details.put("validate", validateDetails);

		JSONObject publishDetails = new JSONObject();
		JSONArray publishProcessedCount = new JSONArray();
		JSONObject publishProCountSuccess = new JSONObject();
		publishProCountSuccess.put("type", "success");
		publishProCountSuccess.put("count", publishSuccess);
		publishProcessedCount.put(publishProCountSuccess);
		JSONObject publishProCountFailure = new JSONObject();
		publishProCountFailure.put("type", "failed");
		publishProCountFailure.put("count", publishError);
		publishProcessedCount.put(publishProCountFailure);
		publishDetails.put("processedCount", publishProcessedCount);
		details.put("publish", publishDetails);

		if (ingestComplete == 1 && (ingestSuccess + ingestError == count)) {
			// pseudo ingest complete
			v1 = true;
		}

		if (v1 == true && (validateError + validateSuccess >= ingestSuccess)) {
			// pseudo validate complete
			v2 = true;
		}

		if (v2 == true && (publishError + publishSuccess >= validateSuccess)) {
			// pseudo publish complete
			v3 = true;

		}

		if (v1 && v2 && v3) {

			StatusEnum taskStatus = StatusEnum.completed;
			
			log.info("deleting redis entry for pseudo ingest : serviceRequestNumber :: " + serviceRequestNumber);
			taskTrackerRedisDao.delete(serviceRequestNumber);
			
			double successRate = (publishSuccess/count)*100 ;
			
			log.info("serviceRequestNumber :: " + serviceRequestNumber + "success rate :: " + successRate);
			
			if(successRate <= successThreshold) {
				
				log.info(" pseudo ingest failed serviceRequestNumber :: " + serviceRequestNumber);
				taskStatus = com.ulca.dataset.model.TaskTracker.StatusEnum.failed;
				processTaskTrackerService.updateTaskTrackerWithDetailsAndEndTime(serviceRequestNumber, ToolEnum.pseudo,
						taskStatus, details.toString());
				
			}else {
				processTaskTrackerService.updateTaskTrackerWithDetailsAndEndTime(serviceRequestNumber, ToolEnum.pseudo,
						taskStatus, details.toString());
				
				DatasetIngest datasetIngest = new DatasetIngest();
				datasetIngest.setMode(DatasetConstants.INGEST_REAL_MODE);
				datasetIngest.setBaseLocation(baseLocation);
				datasetIngest.setMd5hash(md5hash);
				datasetIngest.setServiceRequestNumber(serviceRequestNumber);
				
				datasetIngestKafkaTemplate.send(datasetIngestTopic, datasetIngest);
				//datasetIngestKafkaTemplate.send(datasetIngestTopic,0,null, datasetIngest);
			}

		} else {
			processTaskTrackerService.updateTaskTrackerWithDetails(serviceRequestNumber, ToolEnum.pseudo,
					com.ulca.dataset.model.TaskTracker.StatusEnum.inprogress, details.toString());
		}

	}

	public void realIngestUpdate(Map<String, String> val) {

		String serviceRequestNumber = val.containsKey("serviceRequestNumber") ? val.get("serviceRequestNumber") + ""
				: null;

		Integer ingestComplete = val.containsKey("ingestComplete") ? Integer.parseInt(val.get("ingestComplete") + "")
				: 0;
		Integer count = val.containsKey("count") ? Integer.parseInt(val.get("count") + "") : 0;
		Integer ingestError = val.containsKey("ingestError") ? Integer.parseInt(val.get("ingestError") + "") : 0;
		Integer ingestSuccess = val.containsKey("ingestSuccess") ? Integer.parseInt(val.get("ingestSuccess") + "") : 0;
		Integer validateError = val.containsKey("validateError") ? Integer.parseInt(val.get("validateError") + "") : 0;
		Integer validateSuccess = val.containsKey("validateSuccess") ? Integer.parseInt(val.get("validateSuccess") + "")
				: 0;
		Integer publishError = val.containsKey("publishError") ? Integer.parseInt(val.get("publishError") + "") : 0;
		Integer publishSuccess = val.containsKey("publishSuccess") ? Integer.parseInt(val.get("publishSuccess") + "")
				: 0;

		boolean v1 = false;
		boolean v2 = false;
		boolean v3 = false;

		JSONObject details = new JSONObject();

		JSONArray processedCount = new JSONArray();

		JSONObject proCountSuccess = new JSONObject();
		proCountSuccess.put("type", "success");
		proCountSuccess.put("count", ingestSuccess);
		processedCount.put(proCountSuccess);

		JSONObject proCountFailure = new JSONObject();

		proCountFailure.put("type", "failed");
		proCountFailure.put("count", ingestError);
		processedCount.put(proCountFailure);
		details.put("processedCount", processedCount);
		details.put("timeStamp", new Date().toString());

		if (ingestComplete == 1 && (ingestSuccess + ingestError == count)) {
			// update the end time for ingest
			v1 = true;
			processTaskTrackerService.updateTaskTrackerWithDetailsAndEndTime(serviceRequestNumber, ToolEnum.ingest,
					com.ulca.dataset.model.TaskTracker.StatusEnum.completed, details.toString());

		} else {

			processTaskTrackerService.updateTaskTrackerWithDetails(serviceRequestNumber, ToolEnum.ingest,
					com.ulca.dataset.model.TaskTracker.StatusEnum.inprogress, details.toString());
		}
		
		
		
		if(val.containsKey("validateSuccessSeconds")) {
			proCountSuccess.put("validateSuccessSeconds", val.get("validateSuccessSeconds"));
		}
		if(val.containsKey("validateErrorSeconds")) {
			proCountFailure.put("validateErrorSeconds", val.get("validateErrorSeconds"));
		}
		proCountSuccess.put("count", validateSuccess);
		proCountFailure.put("count", validateError);

		if (v1 == true && (validateError + validateSuccess >= ingestSuccess)) {
			// update the end time for validate
			v2 = true;

			processTaskTrackerService.updateTaskTrackerWithDetailsAndEndTime(serviceRequestNumber, ToolEnum.validate,
					com.ulca.dataset.model.TaskTracker.StatusEnum.completed, details.toString());
		} else {
			if (validateSuccess > 0 || validateError > 0)
				processTaskTrackerService.updateTaskTrackerWithDetails(serviceRequestNumber, ToolEnum.validate,
						com.ulca.dataset.model.TaskTracker.StatusEnum.inprogress, details.toString());
		}

		if(val.containsKey("publishSuccessSeconds")) {
			proCountSuccess.put("publishSuccessSeconds", val.get("publishSuccessSeconds"));
		}
		if(val.containsKey("publishErrorSeconds")) {
			proCountFailure.put("publishErrorSeconds", val.get("publishErrorSeconds"));
		}
		//remove the values for validateSuccessSeconds and validateErrorSeconds
		if(proCountSuccess.has("validateSuccessSeconds")) {
			proCountSuccess.remove("validateSuccessSeconds");
		}
		if(proCountFailure.has("validateErrorSeconds")) {
			proCountFailure.remove("validateErrorSeconds");
		}
		
		proCountSuccess.put("count", publishSuccess);
		proCountFailure.put("count", publishError);

		if (v2 == true && (publishError + publishSuccess >= validateSuccess)) {
			// update the end time for publish
			v3 = true;

			processTaskTrackerService.updateTaskTrackerWithDetailsAndEndTime(serviceRequestNumber, ToolEnum.publish,
					com.ulca.dataset.model.TaskTracker.StatusEnum.completed, details.toString());
		} else {
			if (publishSuccess > 0 || publishError > 0)
				processTaskTrackerService.updateTaskTrackerWithDetails(serviceRequestNumber, ToolEnum.publish,
						com.ulca.dataset.model.TaskTracker.StatusEnum.inprogress, details.toString());
		}

		if (v1 && v2 && v3) {

			log.info("deleting for serviceRequestNumber :: " + serviceRequestNumber);

			taskTrackerRedisDao.delete(serviceRequestNumber);
			processTaskTrackerService.updateProcessTracker(serviceRequestNumber, ProcessTracker.StatusEnum.completed);
			
			//upload submitted-datasets file to object store and delete the file
			datasetFileService.datasetAfterIngestCleanJob(serviceRequestNumber);
		}

	}

}
