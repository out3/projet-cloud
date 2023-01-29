package wc;

import java.util.Arrays;
import org.apache.spark.SparkConf;
import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import scala.Tuple2;

public class WordCount {
	public static void main(String[] args) {
	    String filename = args[0];
		String inputFile = filename;
		String outputFile = "/opt/bitnami/spark/tmp/result";
		SparkConf conf = new SparkConf().setAppName("WordCount");
		try (JavaSparkContext sc = new JavaSparkContext(conf)) {
			long t1 = System.currentTimeMillis();

			JavaRDD<String> data =
					sc.textFile(inputFile)
						.flatMap(s -> Arrays.asList(s.split(" "))
						.iterator());
			
			JavaPairRDD<String, Integer> counts =
					data.mapToPair(w -> new Tuple2<String, Integer>(w,1))
						.reduceByKey((c1,c2) -> c1 + c2); //add func
			counts.saveAsTextFile(outputFile);

			long t2 = System.currentTimeMillis();
			System.out.println("======================");
			System.out.println("time in ms :"+(t2-t1));
		}
		System.out.println("======================");
	}
}
