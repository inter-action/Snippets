package model

import java.util.Date

import org.joda.time.DateTime

import play.api.Logger

import scala.collection.JavaConverters._
import scala.reflect.ClassTag

/*
from repo: git@github.com:longcao/merseyside.git

feature:
  recursive conversion
  safely get convert variable by desired type  
 */


object Yaml {
  def empty = Yaml(Map.empty)

  def parseYaml(any: AnyRef): AnyRef = any match {
    case map: java.util.Map[String, AnyRef] => Yaml(map.asScala.toMap.mapValues(parseYaml))
    case list: java.util.List[AnyRef] => list.asScala.toList.map(parseYaml)
    case s: String => s
    case n: Number => n
    case b: java.lang.Boolean => b
    case d: Date => new DateTime(d)
    case null => null
    case e => throw new Exception(s"unable to parse object ${e.getClass}")
  }

  def parseFrontMatter(s: String): Yaml = {
    val yaml = new org.yaml.snakeyaml.Yaml().load(s)
    parseYaml(yaml) match {
      case y: Yaml => y
      case e =>
        Logger.warn("YAML didn't parse nicely: " + e)
        Yaml.empty
    }
  }
}

case class Yaml(map: Map[String, AnyRef]) {
  def get[T: ClassTag](key: String): Option[T] = {
    val ct = implicitly[ClassTag[T]]// class Tag of T

    map.get(key).flatMap {
      // ct is a instance of ClassTag[T]
      // ct.runTimeClass return java.lang.class
      case t if ct.runtimeClass.isInstance(t) => Some(t.asInstanceOf[T])
      case other =>
        Logger.warn("Ignoring value for key " + key + ", expected " + ct + " but was " + other)
        None
    }
  }
}
